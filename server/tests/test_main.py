from src.core.config import settings
from src.core.mongo import mongo_manager

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    mongo_status = "connected" if mongo_manager.client is not None else "disconnected"
    assert response.json() == {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "databases": {
            "postgres": "connected",
            "mongodb": mongo_status,
        },
    }