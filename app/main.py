import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.config import settings
from app.database import Base, engine
from app.logging_config import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware

setup_logging(settings.log_level)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Starting %s", settings.app_name)
    yield
    logger.info("Shutting down")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Finance Dashboard API running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
