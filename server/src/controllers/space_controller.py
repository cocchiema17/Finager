from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.controllers.deps import get_current_user
from src.models.user import User
from src.schemas.space_schema import SpaceCreate, SpaceUpdate, SpaceResponse, SpaceListResponse
from src.services.space_service import SpaceService

router = APIRouter(prefix="/api/spaces", tags=["Spaces"])


@router.get("", response_model=SpaceListResponse)
def get_user_spaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    spaces = SpaceService.list_spaces(db, user.id)
    return {"value": spaces}


@router.post("", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
def create_space(
    payload: SpaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SpaceService.create_space(db, user.id, payload)

@router.put("/{space_id}", response_model=SpaceResponse)
def update_space(
    space_id: int,
    payload: SpaceUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SpaceService.update_space(db, space_id, user.id, payload)


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(
    space_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    SpaceService.delete_space(db, space_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)