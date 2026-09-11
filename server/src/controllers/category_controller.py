from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.controllers.deps import get_current_user
from src.models.user import User
from src.schemas.category_schema import CategoryCreate, CategoryResponse, CategoryListResponse
from src.services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=CategoryListResponse)
def get_user_categories(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = CategoryService.list_categories(db, user.id)
    return {"value": categories}


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CategoryService.create_category(db, user.id, payload)


@router.delete("/{space_id}/{category_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    space_id: int,
    category_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    CategoryService.delete_category(db, user.id, space_id, category_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)