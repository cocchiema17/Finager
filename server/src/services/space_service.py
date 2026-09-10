from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from src.repositories.space_repository import SpaceRepository
from src.schemas.space_schema import SpaceCreate, SpaceUpdate
from src.models.space import Space


class SpaceService:
    @staticmethod
    def list_spaces(db: Session, user_id: UUID) -> list[Space]:
        return SpaceRepository.get_by_user_id(db, user_id)

    @staticmethod
    def create_space(db: Session, user_id: UUID, data: SpaceCreate) -> Space:
        clean_name = data.name.strip()

        # Controllo preventivo sul vincolo di unicità
        existing = SpaceRepository.get_by_name_and_user(db, clean_name, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Space with name {clean_name} already in use",
            )

        try:
            return SpaceRepository.create(db, user_id, clean_name)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Space with name {clean_name} already in use",
            )

    @staticmethod
    def update_space(db: Session, space_id: int, user_id: UUID, data: SpaceUpdate) -> Space:
        space = SpaceRepository.get_by_id(db, space_id)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found",
            )

        # Controllo autorizzazione: l'utente deve possedere questo space
        if space.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this space",
            )

        clean_name = data.name.strip()
        # Verifica se esiste già un altro space con lo stesso nome per questo utente
        duplicate = SpaceRepository.get_by_name_and_user(db, clean_name, user_id)
        if duplicate and duplicate.id != space_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Space with name {clean_name} already in use",
            )

        try:
            return SpaceRepository.update(db, space, clean_name)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Space with name {clean_name} already in use",
            )

    @staticmethod
    def delete_space(db: Session, space_id: int, user_id: UUID) -> None:
        space = SpaceRepository.get_by_id(db, space_id)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found",
            )

        if space.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this space",
            )

        SpaceRepository.delete(db, space)