def test_register_user_success(client):
    payload = {
        "firstName": "Mario",
        "lastName": "Rossi",
        "email": "mario.rossi@example.com",
        "password": "securepassword123",
    }
    response = client.post("/api/auth/signup", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "mario.rossi@example.com"
    assert "id" in data
    # Verifica che la password non venga esposta nel JSON di risposta
    assert "password" not in data
    # Verifica che venga impostato il token di sessione
    assert "token" in data
    # Verifica che il token sia una stringa non vuota
    assert isinstance(data["token"], str) and len(data["token"]) > 20


def test_register_duplicate_email(client):
    payload = {
        "firstName": "Mario",
        "lastName": "Rossi",
        "email": "mario.rossi@example.com",
        "password": "securepassword123",
    }
    # Prima registrazione
    client.post("/api/auth/signup", json=payload)
    # Seconda registrazione con la stessa email
    response = client.post("/api/auth/signup", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already in use"


def test_login_success(client):
    # Registra un utente
    client.post(
        "/api/auth/signup",
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
    response = client.post("/api/auth/signin", json=login_payload)
    assert response.status_code == 200
    assert response.json()["email"] == "luigi.verdi@example.com"
    assert "token" in response.json()
    assert isinstance(response.json()["token"], str) and len(response.json()["token"]) > 20


def test_login_invalid_password(client):
    client.post(
        "/api/auth/signup",
        json={
            "firstName": "Luigi",
            "lastName": "Verdi",
            "email": "luigi.verdi@example.com",
            "password": "mypassword123",
        },
    )

    response = client.post(
        "/api/auth/signin",
        json={"email": "luigi.verdi@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"