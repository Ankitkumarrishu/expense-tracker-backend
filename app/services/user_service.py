from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    total_count = db.execute(select(func.count()).select_from(User)).scalar_one()
    rows = db.execute(select(User).offset(skip).limit(limit).order_by(User.id)).scalars().all()
    return list(rows), int(total_count)


def create_user(db: Session, data: UserCreate) -> User:
    if get_by_email(db, data.email):
        raise ValueError("Email already registered")
    user = User(
        email=data.email,
        full_name=data.full_name,
        role=data.role,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    from app.core.security import verify_password

    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
