from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.models.category import Category
from src.models.space import Space


class CategoryRepository:
    @staticmethod
    def get_by_name_and_space(db: Session, name: str, space_id: int) -> Optional[Category]:
        return db.query(Category).filter(
            Category.name == name,
            Category.spaceId == space_id,
        ).first()

    @staticmethod
    def get_user_categories(db: Session, user_id: UUID) -> list[dict]:
        # SELECT c.*, s.name as "spaceName" FROM category c JOIN space s ON c."spaceId" = s.id WHERE s."userId" = $1
        rows = (
            db.query(Category, Space.name.label("spaceName"))
            .join(Space, Category.spaceId == Space.id)
            .filter(Space.userId == user_id)
            .all()
        )
        result = []
        for cat, space_name in rows:
            result.append({
                "name": cat.name,
                "spaceId": cat.spaceId,
                "color": cat.color,
                "spaceName": space_name,
            })
        return result

    @staticmethod
    def create(db: Session, name: str, space_id: int, color: Optional[str] = None) -> Category:
        category = Category(name=name, spaceId=space_id, color=color)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category: Category) -> None:
        db.delete(category)
        db.commit()