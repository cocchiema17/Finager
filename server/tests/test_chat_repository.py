import uuid
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
from src.schemas.chat_schema import ChatMessage
from src.repositories.chat_repository import ChatRepository


@pytest.fixture
async def mongo_test_db():
    """Connessione a un DB temporaneo 'finager_test_db' pulito alla fine."""
    client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
    test_db = client["finager_test_chat_db"]
    try:
        # Verifica raggiungibilità
        await client.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB locale non disponibile su " + settings.MONGO_URI)
    
    yield test_db
    # Cleanup post test
    await client.drop_database("finager_test_chat_db")
    client.close()


@pytest.mark.anyio
async def test_chat_repository_crud(mongo_test_db):
    user_id = uuid.uuid4()

    # 1. Creazione sessione
    session = await ChatRepository.create_session(mongo_test_db, user_id, "Sessione Test")
    assert session["title"] == "Sessione Test"
    assert session["userId"] == user_id
    assert len(session["messages"]) == 0
    session_id = session["id"]

    # 2. Append messaggio User
    user_msg = ChatMessage(role="user", content="Come posso risparmiare sulle bollette?")
    ok_user = await ChatRepository.append_message(mongo_test_db, session_id, user_id, user_msg)
    assert ok_user is True

    # 3. Append messaggio Assistant
    bot_msg = ChatMessage(role="assistant", content="Puoi monitorare le uscite fisse...")
    ok_bot = await ChatRepository.append_message(mongo_test_db, session_id, user_id, bot_msg)
    assert ok_bot is True

    # 4. Recupero e verifica messaggi
    fetched = await ChatRepository.get_session_by_id(mongo_test_db, session_id, user_id)
    assert fetched is not None
    assert len(fetched["messages"]) == 2
    assert fetched["messages"][0]["role"] == "user"
    assert fetched["messages"][1]["role"] == "assistant"

    # 5. Listing sessioni utente
    sessions_list = await ChatRepository.list_user_sessions(mongo_test_db, user_id)
    assert len(sessions_list) == 1
    assert sessions_list[0]["messageCount"] == 2

    # 6. Cancellazione sessione
    deleted = await ChatRepository.delete_session(mongo_test_db, session_id, user_id)
    assert deleted is True

    # 7. Verifica cancellazione
    none_session = await ChatRepository.get_session_by_id(mongo_test_db, session_id, user_id)
    assert none_session is None