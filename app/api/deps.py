from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import Permission, get_user_by_id, require_permission
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_error
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise credentials_error from None
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_dashboard_user(user: CurrentUser) -> User:
    require_permission(user, Permission.DASHBOARD_READ)
    return user


def require_records_reader(user: CurrentUser) -> User:
    require_permission(user, Permission.RECORDS_READ)
    return user


def require_records_writer(user: CurrentUser) -> User:
    require_permission(user, Permission.RECORDS_WRITE)
    return user


def require_user_admin(user: CurrentUser) -> User:
    require_permission(user, Permission.USERS_MANAGE)
    return user


DashboardUser = Annotated[User, Depends(require_dashboard_user)]
RecordsReader = Annotated[User, Depends(require_records_reader)]
RecordsWriter = Annotated[User, Depends(require_records_writer)]
UserAdmin = Annotated[User, Depends(require_user_admin)]
