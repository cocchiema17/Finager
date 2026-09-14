from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.schemas.chat_schema import ChatMessage


class ChatRepository:
    COLLECTION_NAME = "chat_sessions"

    @staticmethod
    def _to_session_dict(doc: dict) -> dict:
        """Converte il documento MongoDB nativo nel formato atteso dagli schemi."""
        return {
            "id": str(doc["_id"]),
            "userId": UUID(str(doc["userId"])) if not isinstance(doc["userId"], UUID) else doc["userId"],
            "title": doc.get("title", "Nuova conversazione"),
            "createdAt": doc.get("createdAt"),
            "updatedAt": doc.get("updatedAt"),
            "messages": doc.get("messages", []),
        }

    @classmethod
    async def create_session(
        cls,
        db: AsyncIOMotorDatabase,
        user_id: UUID,
        title: str = "Nuova conversazione",
    ) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "userId": str(user_id),
            "title": title.strip() or "Nuova conversazione",
            "createdAt": now,
            "updatedAt": now,
            "messages": [],
        }
        result = await db[cls.COLLECTION_NAME].insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls._to_session_dict(doc)

    @classmethod
    async def get_session_by_id(
        cls,
        db: AsyncIOMotorDatabase,
        session_id: str,
        user_id: UUID,
    ) -> Optional[dict]:
        try:
            obj_id = ObjectId(session_id)
        except InvalidId:
            return None

        doc = await db[cls.COLLECTION_NAME].find_one({
            "_id": obj_id,
            "userId": str(user_id),
        })
        if not doc:
            return None
        return cls._to_session_dict(doc)

    @classmethod
    async def list_user_sessions(
        cls,
        db: AsyncIOMotorDatabase,
        user_id: UUID,
        limit: int = 50,
    ) -> list[dict]:
        cursor = (
            db[cls.COLLECTION_NAME]
            .find({"userId": str(user_id)})
            .sort("updatedAt", -1)
            .limit(limit)
        )
        sessions = []
        async for doc in cursor:
            summary = {
                "id": str(doc["_id"]),
                "userId": UUID(str(doc["userId"])),
                "title": doc.get("title", "Nuova conversazione"),
                "createdAt": doc.get("createdAt"),
                "updatedAt": doc.get("updatedAt"),
                "messageCount": len(doc.get("messages", [])),
            }
            sessions.append(summary)
        return sessions

    @classmethod
    async def append_message(
        cls,
        db: AsyncIOMotorDatabase,
        session_id: str,
        user_id: UUID,
        message: ChatMessage,
    ) -> bool:
        """Aggiunge atomicamente un messaggio all'array messages e aggiorna updatedAt."""
        try:
            obj_id = ObjectId(session_id)
        except InvalidId:
            return False

        now = datetime.now(timezone.utc)
        msg_dict = message.model_dump()
        # Assicuriamo la serializzazione del timestamp
        if isinstance(msg_dict.get("timestamp"), datetime):
            pass

        result = await db[cls.COLLECTION_NAME].update_one(
            {"_id": obj_id, "userId": str(user_id)},
            {
                "$push": {"messages": msg_dict},
                "$set": {"updatedAt": now},
            },
        )
        return result.modified_count > 0

    @classmethod
    async def update_title(
        cls,
        db: AsyncIOMotorDatabase,
        session_id: str,
        user_id: UUID,
        new_title: str,
    ) -> bool:
        try:
            obj_id = ObjectId(session_id)
        except InvalidId:
            return False

        result = await db[cls.COLLECTION_NAME].update_one(
            {"_id": obj_id, "userId": str(user_id)},
            {"$set": {"title": new_title.strip(), "updatedAt": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    @classmethod
    async def delete_session(
        cls,
        db: AsyncIOMotorDatabase,
        session_id: str,
        user_id: UUID,
    ) -> bool:
        try:
            obj_id = ObjectId(session_id)
        except InvalidId:
            return False

        result = await db[cls.COLLECTION_NAME].delete_one({
            "_id": obj_id,
            "userId": str(user_id),
        })
        return result.deleted_count > 0