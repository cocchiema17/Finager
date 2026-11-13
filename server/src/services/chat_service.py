import json
from typing import AsyncGenerator
from uuid import UUID
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session
from src.repositories.chat_repository import ChatRepository
from src.schemas.chat_schema import ChatMessage
from src.services.ollama_service import OllamaService
from src.services.financial_context_service import FinancialContextService


class ChatService:
    @staticmethod
    async def create_session(
        db: AsyncIOMotorDatabase,
        user_id: UUID,
        title: str,
    ) -> dict:
        return await ChatRepository.create_session(db, user_id, title)

    @staticmethod
    async def list_sessions(
        db: AsyncIOMotorDatabase,
        user_id: UUID,
    ) -> list[dict]:
        return await ChatRepository.list_user_sessions(db, user_id)

    @staticmethod
    async def get_session(
        db: AsyncIOMotorDatabase,
        session_id: str,
        user_id: UUID,
    ) -> dict:
        session = await ChatRepository.get_session_by_id(db, session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessione di chat non trovata",
            )
        return session

    @staticmethod
    async def delete_session(
        db: AsyncIOMotorDatabase,
        session_id: str,
        user_id: UUID,
    ) -> None:
        deleted = await ChatRepository.delete_session(db, session_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessione di chat non trovata",
            )

    @staticmethod
    async def stream_chat_response(
        mongo_db: AsyncIOMotorDatabase,
        sql_db: Session,
        session_id: str,
        user_id: UUID,
        prompt: str,
    ) -> AsyncGenerator[str, None]:
        # 1. Verifica che la sessione esista e appartenga all'utente
        session = await ChatRepository.get_session_by_id(mongo_db, session_id, user_id)
        if not session:
            yield f"data: {json.dumps({'error': 'Sessione non trovata', 'done': True})}\n\n"
            return

        # 2. Estrae lo snapshot finanziario aggiornato da PostgreSQL
        financial_context = FinancialContextService.build_user_financial_context(sql_db, user_id)

        # 3. Salva immediatamente il messaggio dell'utente su MongoDB
        user_msg = ChatMessage(role="user", content=prompt.strip())
        await ChatRepository.append_message(mongo_db, session_id, user_id, user_msg)

        # 4. Estrai la cronologia preesistente per il contesto
        history = [ChatMessage(**m) for m in session.get("messages", [])]

        # 5. Stream verso il client con accumulo della risposta
        full_assistant_reply = []

        async for chunk_json in OllamaService.stream_chat_completion(history, prompt.strip(), financial_context):
            data = json.loads(chunk_json)
            content = data.get("content", "")
            if content:
                full_assistant_reply.append(content)

            # Invia l'evento SSE nel formato standard: data: <payload>\n\n
            yield f"data: {chunk_json}\n\n"

        # 5. A stream concluso, salva la risposta dell'assistente nel DB
        assistant_text = "".join(full_assistant_reply).strip()
        if assistant_text:
            bot_msg = ChatMessage(role="assistant", content=assistant_text)
            await ChatRepository.append_message(mongo_db, session_id, user_id, bot_msg)

            # Se era il primo scambio, aggiorniamo il titolo con una sintesi del prompt
            if len(session.get("messages", [])) == 0:
                short_title = prompt.strip()[:40] + ("..." if len(prompt.strip()) > 40 else "")
                await ChatRepository.update_title(mongo_db, session_id, user_id, short_title)