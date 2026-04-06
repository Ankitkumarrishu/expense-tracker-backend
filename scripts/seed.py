"""Create demo users and sample financial records. Run from project root: python scripts/seed.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models.financial_record import EntryType, FinancialRecord
from app.models.user import User, UserRole
from app.core.security import hash_password
from datetime import date, timedelta
from decimal import Decimal


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.execute(select(User).where(User.email == "admin@example.com")).scalar_one_or_none():
            print("Seed already applied (admin@example.com exists). Skipping.")
            return

        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            role=UserRole.ADMIN,
            hashed_password=hash_password("admin12345"),
        )
        analyst = User(
            email="analyst@example.com",
            full_name="Analyst User",
            role=UserRole.ANALYST,
            hashed_password=hash_password("analyst12345"),
        )
        viewer = User(
            email="viewer@example.com",
            full_name="Viewer User",
            role=UserRole.VIEWER,
            hashed_password=hash_password("viewer12345"),
        )
        db.add_all([admin, analyst, viewer])
        db.commit()
        db.refresh(admin)

        today = date.today()
        samples = [
            FinancialRecord(
                amount=Decimal("5000.00"),
                type=EntryType.INCOME,
                category="Salary",
                entry_date=today.replace(day=1),
                notes="Monthly salary",
                created_by_id=admin.id,
            ),
            FinancialRecord(
                amount=Decimal("120.50"),
                type=EntryType.EXPENSE,
                category="Utilities",
                entry_date=today - timedelta(days=5),
                notes="Electricity",
                created_by_id=admin.id,
            ),
            FinancialRecord(
                amount=Decimal("45.00"),
                type=EntryType.EXPENSE,
                category="Food",
                entry_date=today - timedelta(days=2),
                notes="Groceries",
                created_by_id=admin.id,
            ),
            FinancialRecord(
                amount=Decimal("200.00"),
                type=EntryType.INCOME,
                category="Freelance",
                entry_date=today - timedelta(days=10),
                notes="Side project",
                created_by_id=admin.id,
            ),
        ]
        db.add_all(samples)
        db.commit()
        print("Seed complete.")
        print("  admin@example.com / admin12345 (admin)")
        print("  analyst@example.com / analyst12345 (analyst)")
        print("  viewer@example.com / viewer12345 (viewer)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
