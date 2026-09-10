from src.core.config import settings

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}