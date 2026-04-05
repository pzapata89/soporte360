from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Category]:
    query = db.query(Category)
    if active_only:
        query = query.filter(Category.is_active == True)
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    db_category = Category(
        name=category_data.name,
        description=category_data.description,
        is_active=category_data.is_active
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category: Category, category_data: CategoryUpdate) -> Category:
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category
