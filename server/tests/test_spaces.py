def test_create_and_get_spaces(client):
    reg_payload = {
        "firstName": "Anna",
        "lastName": "Verdi",
        "email": "anna.verdi@example.com",
        "password": "securepassword123",
    }
    client.post("/api/auth/register", json=reg_payload)

    # 1. Creazione Space
    create_res = client.post("/api/spaces", json={"name": "Personale"})
    assert create_res.status_code == 201
    space_data = create_res.json()
    assert space_data["name"] == "Personale"
    assert "id" in space_data

    # 2. Lettura lista Spaces
    get_res = client.get("/api/spaces")
    assert get_res.status_code == 200
    res_json = get_res.json()
    assert len(res_json["value"]) == 1
    assert res_json["value"][0]["name"] == "Personale"


def test_update_and_delete_space(client):
    client.post(
        "/api/auth/register",
        json={
            "firstName": "Giovanni",
            "lastName": "Bianchi",
            "email": "giovanni.bianchi@example.com",
            "password": "securepassword123",
        },
    )

    # Crea Space
    create_res = client.post("/api/spaces", json={"name": "Vecchia Casa"})
    assert create_res.status_code == 201
    space_id = create_res.json()["id"]

    # Modifica (PUT)
    update_res = client.put(f"/api/spaces/{space_id}", json={"name": "Nuova Casa"})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Nuova Casa"

    # Eliminazione (DELETE)
    del_res = client.delete(f"/api/spaces/{space_id}")
    assert del_res.status_code == 204

    # Verifica eliminazione
    get_res = client.get("/api/spaces")
    assert len(get_res.json()["value"]) == 0


def test_create_duplicate_space_name(client):
    client.post(
        "/api/auth/register",
        json={
            "firstName": "Marco",
            "lastName": "Neri",
            "email": "marco.neri@example.com",
            "password": "securepassword123",
        },
    )

    res1 = client.post("/api/spaces", json={"name": "Lavoro"})
    assert res1.status_code == 201

    res2 = client.post("/api/spaces", json={"name": "Lavoro"})
    assert res2.status_code == 400
    assert "already in use" in res2.json()["detail"]


def test_unauthenticated_access(client):
    res = client.get("/api/spaces")
    assert res.status_code == 401