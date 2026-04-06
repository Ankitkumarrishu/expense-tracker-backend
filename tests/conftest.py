from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.financial_record import EntryType, FinancialRecord
from app.models.user import User, UserRole


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    admin = User(
        email="admin@test.com",
        full_name="Admin",
        role=UserRole.ADMIN,
        hashed_password=hash_password("admin12345"),
    )
    analyst = User(
        email="analyst@test.com",
        full_name="Analyst",
        role=UserRole.ANALYST,
        hashed_password=hash_password("analyst12345"),
    )
    viewer = User(
        email="viewer@test.com",
        full_name="Viewer",
        role=UserRole.VIEWER,
        hashed_password=hash_password("viewer12345"),
    )
    db.add_all([admin, analyst, viewer])
    db.commit()
    db.refresh(admin)
    db.add(
        FinancialRecord(
            amount=Decimal("100.00"),
            type=EntryType.INCOME,
            category="Test",
            entry_date=date.today(),
            notes="seed",
            created_by_id=admin.id,
        )
    )
    db.commit()
    db.close()

    def override_get_db():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        tc = TestClient(app, lifespan="off")
    except TypeError:
        tc = TestClient(app)
    with tc as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
