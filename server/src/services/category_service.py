from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from src.repositories.category_repository import CategoryRepository
from src.repositories.space_repository import SpaceRepository
from src.schemas.category_schema import CategoryCreate, CategoryResponse
from src.models.category import Category


class CategoryService:
    @staticmethod
    def list_categories(db: Session, user_id: UUID) -> list[dict]:
        return CategoryRepository.get_user_categories(db, user_id)

    @staticmethod
    def create_category(db: Session, user_id: UUID, data: CategoryCreate) -> CategoryResponse:
        clean_name = data.name.strip()

        # 1. Verifica che lo Space esista e appartenga all'utente loggato
        space = SpaceRepository.get_by_id(db, data.spaceId)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found",
            )
        if space.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add category to this space",
            )

        # 2. Controllo duplicati (chiave primaria composta name + spaceId)
        existing = CategoryRepository.get_by_name_and_space(db, clean_name, data.spaceId)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{clean_name}' already exists in this space",
            )

        try:
            cat = CategoryRepository.create(db, clean_name, data.spaceId, data.color)
            return CategoryResponse(
                name=cat.name,
                spaceId=cat.spaceId,
                color=cat.color,
                spaceName=space.name,
            )
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e.orig)}",
            )

    @staticmethod
    def delete_category(db: Session, user_id: UUID, space_id: int, category_name: str) -> None:
        space = SpaceRepository.get_by_id(db, space_id)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found",
            )
        if space.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete category from this space",
            )

        cat = CategoryRepository.get_by_name_and_space(db, category_name, space_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        CategoryRepository.delete(db, cat)