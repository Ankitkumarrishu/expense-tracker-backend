from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, UserAdmin
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("", response_model=list[UserOut])
def list_users(
    admin: UserAdmin,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    users, _ = user_service.list_users(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(admin: UserAdmin, db: Annotated[Session, Depends(get_db)], body: UserCreate):
    try:
        return user_service.create_user(db, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/{user_id}", response_model=UserOut)
def get_user(admin: UserAdmin, db: Annotated[Session, Depends(get_db)], user_id: int):
    user = user_service.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    admin: UserAdmin,
    current: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    user_id: int,
    body: UserUpdate,
):
    user = user_service.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current.id and body.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )
    return user_service.update_user(db, user, body)
