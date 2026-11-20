def test_create_and_get_spaces(client):
    reg_payload = {
        "firstName": "Anna",
        "lastName": "Verdi",
        "email": "anna.verdi@example.com",
        "password": "securepassword123",
    }
    reg_res = client.post("/api/auth/signup", json=reg_payload)
    token = reg_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verifica che il conto "Principale" sia stato creato automaticamente dopo l'accesso
    login_payload = {
        "email": "anna.verdi@example.com",
        "password": "securepassword123",
    }
    login_res = client.post("/api/auth/signin", json=login_payload)
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    get_res = client.get("/api/spaces", headers=headers)
    assert get_res.status_code == 200
    res_json = get_res.json()
    assert len(res_json["value"]) == 1
    assert res_json["value"][0]["name"] == "Principale"

    # Tentativo di creare un altro conto con lo stesso nome "Principale" dovrebbe fallire
    dup_res = client.post("/api/spaces", json={"name": "Principale"}, headers=headers)
    assert dup_res.status_code == 400

    # Tentativo di rinominare ed eliminare il conto "Principale" dovrebbe fallire
    space_id = res_json["value"][0]["id"]
    update_res = client.put(f"/api/spaces/{space_id}", json={"name": "Nuovo Nome"}, headers=headers)
    assert update_res.status_code == 400
    assert "The 'Principale' space cannot be renamed" in update_res.json()["detail"]
    delete_res = client.delete(f"/api/spaces/{space_id}", headers=headers)
    assert delete_res.status_code == 400
    assert "The 'Principale' space cannot be deleted" in delete_res.json()["detail"]

    # 1. Creazione Space
    create_res = client.post("/api/spaces", json={"name": "Personale"}, headers=headers)
    assert create_res.status_code == 201, create_res.text
    space_data = create_res.json()
    assert space_data["name"] == "Personale"
    assert "id" in space_data

    # 2. Lettura lista Spaces
    get_res = client.get("/api/spaces", headers=headers)
    assert get_res.status_code == 200
    res_json = get_res.json()
    assert len(res_json["value"]) == 2
    assert res_json["value"][1]["name"] == "Personale"


def test_update_and_delete_space(client):
    reg_res = client.post(
        "/api/auth/signup",
        json={
            "firstName": "Giovanni",
            "lastName": "Bianchi",
            "email": "giovanni.bianchi@example.com",
            "password": "securepassword123",
        },
    )

    # Esegue l'accesso per ottenere il token e verificare la creazione automatica del conto "Principale"
    login_payload = {
        "email": "giovanni.bianchi@example.com",
        "password": "securepassword123",
    }
    login_res = client.post("/api/auth/signin", json=login_payload)
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Crea Space
    create_res = client.post("/api/spaces", json={"name": "Vecchia Casa"}, headers=headers)
    assert create_res.status_code == 201
    space_id = create_res.json()["id"]

    # Modifica (PUT)
    update_res = client.put(f"/api/spaces/{space_id}", json={"name": "Nuova Casa"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Nuova Casa"

    # Eliminazione (DELETE)
    del_res = client.delete(f"/api/spaces/{space_id}", headers=headers)
    assert del_res.status_code == 204

    # Verifica eliminazione
    get_res = client.get("/api/spaces", headers=headers)
    assert len(get_res.json()["value"]) == 1  # Solo il conto "Principale" rimane


def test_create_duplicate_space_name(client):
    reg_res = client.post(
        "/api/auth/signup",
        json={
            "firstName": "Marco",
            "lastName": "Neri",
            "email": "marco.neri@example.com",
            "password": "securepassword123",
        },
    )
    # Esegue l'accesso per ottenere il token e verificare la creazione automatica del conto "Principale"
    login_payload = {
        "email": "marco.neri@example.com",
        "password": "securepassword123",
    }
    login_res = client.post("/api/auth/signin", json=login_payload)
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res1 = client.post("/api/spaces", json={"name": "Lavoro"}, headers=headers)
    assert res1.status_code == 201

    res2 = client.post("/api/spaces", json={"name": "Lavoro"}, headers=headers)
    assert res2.status_code == 400
    assert "already in use" in res2.json()["detail"]


def test_unauthenticated_access(client):
    res = client.get("/api/spaces")
    assert res.status_code == 401