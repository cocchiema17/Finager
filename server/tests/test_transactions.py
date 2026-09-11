def test_create_transaction_and_auto_category(client):
    # Registra utente e crea space
    reg_res = client.post(
        "/api/auth/register",
        json={
            "firstName": "Giacomo",
            "lastName": "Leopardi",
            "email": "giacomo@example.com",
            "password": "password123",
        },
    )
    token = reg_res.cookies.get("session")
    headers = {"Authorization": f"Bearer {token}"}

    space_res = client.post("/api/spaces", json={"name": "Casa"}, headers=headers)
    space_id = space_res.json()["id"]

    # 1. Crea transazione (spesa negativa)
    tx_payload = {
        "title": "Supermercato Conad",
        "description": "Spesa settimanale alimentari",
        "date": "2026-03-01",
        "categoryName": "Alimentari",
        "color": "#4CAF50",
        "spaceId": space_id,
        "value": -54.20,
    }
    tx_res = client.post("/api/transactions", json=tx_payload, headers=headers)
    assert tx_res.status_code == 201, tx_res.text
    tx_data = tx_res.json()
    assert tx_data["title"] == "Supermercato Conad"
    assert tx_data["type"] == "expense"
    assert tx_data["value"] == -54.20
    tx_id = tx_data["id"]

    # 2. Verifica che la categoria 'Alimentari' sia stata creata automaticamente
    cat_res = client.get("/api/categories", headers=headers)
    assert cat_res.status_code == 200
    categories = cat_res.json()["value"]
    assert any(c["name"] == "Alimentari" and c["spaceId"] == space_id for c in categories)

    # 3. Verifica listing transazioni con ricerca per testo
    search_res = client.get("/api/transactions?search=Conad", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["totalElements"] == 1
    assert search_data["value"][0]["id"] == tx_id

    # 4. Modifica transazione (PATCH)
    patch_payload = {
        "title": "Supermercato Coop",
        "description": "Spesa modificata",
        "date": "2026-03-02",
        "value": -60.0,
    }
    patch_res = client.patch(f"/api/transactions/{tx_id}", json=patch_payload, headers=headers)
    assert patch_res.status_code == 204

    # 5. Cancellazione transazione (DELETE)
    del_res = client.delete(f"/api/transactions/{tx_id}", headers=headers)
    assert del_res.status_code == 204

    # 6. Verifica lista vuota
    empty_res = client.get("/api/transactions", headers=headers)
    assert empty_res.json()["totalElements"] == 0