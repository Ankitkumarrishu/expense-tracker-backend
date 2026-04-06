from fastapi import APIRouter

from . import auth, dashboard, records, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
