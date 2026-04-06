from enum import IntEnum

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class Permission(IntEnum):
    DASHBOARD_READ = 1
    RECORDS_READ = 2
    RECORDS_WRITE = 3
    USERS_MANAGE = 4


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.VIEWER: frozenset({Permission.DASHBOARD_READ}),
    UserRole.ANALYST: frozenset({Permission.DASHBOARD_READ, Permission.RECORDS_READ}),
    UserRole.ADMIN: frozenset(
        {
            Permission.DASHBOARD_READ,
            Permission.RECORDS_READ,
            Permission.RECORDS_WRITE,
            Permission.USERS_MANAGE,
        }
    ),
}


def role_has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def require_active_user(user: User) -> None:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")


def require_permission(user: User, permission: Permission) -> None:
    require_active_user(user)
    if not role_has_permission(user.role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this action",
        )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
