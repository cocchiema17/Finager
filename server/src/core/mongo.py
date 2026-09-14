import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.core.config import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


mongo_manager = MongoDBManager()


async def connect_to_mongo() -> None:
    """Inizializza la connessione a MongoDB con Motor e verifica con un ping."""
    logger.info("Connessione a MongoDB in corso...")
    mongo_manager.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000,  # 5 secondi di timeout per evitare blocchi prolungati
    )
    mongo_manager.db = mongo_manager.client[settings.MONGO_DB_NAME]
    
    try:
        # Ping di verifica
        await mongo_manager.client.admin.command("ping")
        logger.info(f"Connesso a MongoDB con successo (DB: '{settings.MONGO_DB_NAME}')")
    except Exception as e:
        logger.warning(f"Attenzione: Impossibile raggiungere MongoDB su {settings.MONGO_URI}: {e}")


async def close_mongo_connection() -> None:
    """Chiude in sicurezza il pool di connessioni Motor allo spegnimento."""
    if mongo_manager.client:
        logger.info("Chiusura pool di connessioni MongoDB...")
        mongo_manager.client.close()
        logger.info("Connessioni MongoDB chiuse con successo.")


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Dependency per iniettare l'istanza del database MongoDB asincrono."""
    if mongo_manager.db is None:
        raise RuntimeError("MongoDB client non inizializzato.")
    return mongo_manager.db