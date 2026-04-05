from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: UserCreate) -> User:
    db_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=user_data.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_users_bulk(db: Session, users_data: List[UserCreate]) -> List[User]:
    db_users = []
    for user_data in users_data:
        db_user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=user_data.is_active
        )
        db.add(db_user)
        db_users.append(db_user)
    db.commit()
    for user in db_users:
        db.refresh(user)
    return db_users


def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def activate_user(db: Session, user: User) -> User:
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> User:
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def get_active_technicians(db: Session) -> List[User]:
    """Get active technicians ordered by their current ticket load"""
    return db.query(User).filter(
        User.role == UserRole.TECNICO,
        User.is_active == True
    ).all()
