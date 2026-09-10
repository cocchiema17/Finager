from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.models.space import Space


class SpaceRepository:
    @staticmethod
    def get_by_id(db: Session, space_id: int) -> Optional[Space]:
        return db.query(Space).filter(Space.id == space_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID) -> list[Space]:
        return db.query(Space).filter(Space.userId == user_id).order_by(Space.createdAt.asc()).all()

    @staticmethod
    def get_by_name_and_user(db: Session, name: str, user_id: UUID) -> Optional[Space]:
        return db.query(Space).filter(Space.name == name, Space.userId == user_id).first()

    @staticmethod
    def create(db: Session, user_id: UUID, name: str) -> Space:
        space = Space(name=name, userId=user_id)
        db.add(space)
        db.commit()
        db.refresh(space)
        return space

    @staticmethod
    def update(db: Session, space: Space, new_name: str) -> Space:
        space.name = new_name
        db.commit()
        db.refresh(space)
        return space

    @staticmethod
    def delete(db: Session, space: Space) -> None:
        db.delete(space)
        db.commit()