def test_register_user_success(client):
    payload = {
        "firstName": "Mario",
        "lastName": "Rossi",
        "email": "mario.rossi@example.com",
        "password": "securepassword123",
    }
    response = client.post("/api/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "mario.rossi@example.com"
    assert "id" in data
    # Verifica che la password non venga esposta nel JSON di risposta
    assert "password" not in data
    # Verifica che venga impostato il cookie di sessione
    assert "session" in response.cookies


def test_register_duplicate_email(client):
    payload = {
        "firstName": "Mario",
        "lastName": "Rossi",
        "email": "mario.rossi@example.com",
        "password": "securepassword123",
    }
    # Prima registrazione
    client.post("/api/auth/register", json=payload)
    # Seconda registrazione con la stessa email
    response = client.post("/api/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already in use"


def test_login_success(client):
    # Registra un utente
    client.post(
        "/api/auth/register",
        json={
            "firstName": "Luigi",
            "lastName": "Verdi",
            "email": "luigi.verdi@example.com",
            "password": "mypassword123",
        },
    )

    # Tenta il login
    login_payload = {
        "email": "luigi.verdi@example.com",
        "password": "mypassword123",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    assert response.json()["email"] == "luigi.verdi@example.com"
    assert "session" in response.cookies


def test_login_invalid_password(client):
    client.post(
        "/api/auth/register",
        json={
            "firstName": "Luigi",
            "lastName": "Verdi",
            "email": "luigi.verdi@example.com",
            "password": "mypassword123",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "luigi.verdi@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"