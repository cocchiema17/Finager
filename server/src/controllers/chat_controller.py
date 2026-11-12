from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.core.mongo import get_mongo_db
from src.controllers.deps import get_current_user
from src.models.user import User
from src.schemas.chat_schema import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionSummary,
    ChatPromptRequest,
)
from src.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat & LLM"])


@router.get("/sessions", response_model=list[ChatSessionSummary])
async def list_chat_sessions(
    user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    """Restituisce l'elenco riassuntivo delle conversazioni dell'utente."""
    return await ChatService.list_sessions(mongo_db, user.id)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate,
    user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    """Crea una nuova sessione di chat vuota."""
    return await ChatService.create_session(mongo_db, user.id, payload.title or "Nuova conversazione")


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    """Restituisce l'intera cronologia dei messaggi di una sessione specifica."""
    return await ChatService.get_session(mongo_db, session_id, user.id)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: str,
    user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    """Elimina una sessione di chat e tutti i relativi messaggi."""
    await ChatService.delete_session(mongo_db, session_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions/{session_id}/stream")
async def stream_message(
    session_id: str,
    payload: ChatPromptRequest,
    user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    """
    Endpoint SSE (Server-Sent Events) per inviare un prompt e ricevere la risposta in tempo reale da Ollama.
    """
    generator = ChatService.stream_chat_response(
        db=mongo_db,
        session_id=session_id,
        user_id=user.id,
        prompt=payload.message,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disabilita il buffering dei proxy (es. Nginx)
        },
    )