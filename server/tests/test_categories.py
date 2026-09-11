def test_create_and_get_categories(client):
    # Registra utente
    reg_res = client.post(
        "/api/auth/register",
        json={
            "firstName": "Lucia",
            "lastName": "Galli",
            "email": "lucia.galli@example.com",
            "password": "securepassword123",
        },
    )
    token = reg_res.cookies.get("session")
    headers = {"Authorization": f"Bearer {token}"}

    # Crea Space
    space_res = client.post("/api/spaces", json={"name": "Finanze Personali"}, headers=headers)
    space_id = space_res.json()["id"]

    # 1. Crea Categoria
    cat_payload = {
        "name": "Spesa",
        "spaceId": space_id,
        "color": "#FF5733",
    }
    create_cat_res = client.post("/api/categories", json=cat_payload, headers=headers)
    assert create_cat_res.status_code == 201
    data = create_cat_res.json()
    assert data["name"] == "Spesa"
    assert data["spaceId"] == space_id
    assert data["spaceName"] == "Finanze Personali"

    # 2. Get Categorie
    get_res = client.get("/api/categories", headers=headers)
    assert get_res.status_code == 200
    res_list = get_res.json()["value"]
    assert len(res_list) == 1
    assert res_list[0]["name"] == "Spesa"
    assert res_list[0]["spaceName"] == "Finanze Personali"

    # 3. Elimina Categoria
    del_res = client.delete(f"/api/categories/{space_id}/Spesa", headers=headers)
    assert del_res.status_code == 204

    # 4. Verifica lista vuota
    get_empty_res = client.get("/api/categories", headers=headers)
    assert len(get_empty_res.json()["value"]) == 0


def test_create_category_duplicate_in_same_space(client):
    reg_res = client.post(
        "/api/auth/register",
        json={
            "firstName": "Paolo",
            "lastName": "Fontana",
            "email": "paolo.fontana@example.com",
            "password": "securepassword123",
        },
    )
    token = reg_res.cookies.get("session")
    headers = {"Authorization": f"Bearer {token}"}

    space_res = client.post("/api/spaces", json={"name": "Azienda"}, headers=headers)
    space_id = space_res.json()["id"]

    cat_payload = {"name": "Utenze", "spaceId": space_id, "color": "#123456"}
    res1 = client.post("/api/categories", json=cat_payload, headers=headers)
    assert res1.status_code == 201

    # Secondo inserimento stessa categoria nello stesso space
    res2 = client.post("/api/categories", json=cat_payload, headers=headers)
    assert res2.status_code == 400
    assert "already exists in this space" in res2.json()["detail"]


def test_create_category_foreign_space_forbidden(client):
    # Utente 1 crea space
    reg1 = client.post(
        "/api/auth/register",
        json={
            "firstName": "User1",
            "lastName": "Test",
            "email": "user1@example.com",
            "password": "password123",
        },
    )
    token1 = reg1.cookies.get("session")
    s_res = client.post("/api/spaces", json={"name": "Space U1"}, headers={"Authorization": f"Bearer {token1}"})
    u1_space_id = s_res.json()["id"]

    # Utente 2 tenta di inserire categoria nello space di Utente 1
    reg2 = client.post(
        "/api/auth/register",
        json={
            "firstName": "User2",
            "lastName": "Test",
            "email": "user2@example.com",
            "password": "password123",
        },
    )
    token2 = reg2.cookies.get("session")
    headers2 = {"Authorization": f"Bearer {token2}"}

    res = client.post(
        "/api/categories",
        json={"name": "Hacking", "spaceId": u1_space_id, "color": "#000000"},
        headers=headers2,
    )
    assert res.status_code == 403