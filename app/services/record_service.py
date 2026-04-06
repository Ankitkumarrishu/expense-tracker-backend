from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord
from app.schemas.financial_record import FinancialRecordCreate, FinancialRecordFilter, FinancialRecordUpdate


def _base_select():
    return select(FinancialRecord).where(FinancialRecord.is_deleted.is_(False))


def list_records(
    db: Session,
    filters: FinancialRecordFilter,
    page: int,
    page_size: int,
) -> tuple[list[FinancialRecord], int]:
    conditions = [FinancialRecord.is_deleted.is_(False)]
    if filters.type is not None:
        conditions.append(FinancialRecord.type == filters.type)
    if filters.category is not None:
        conditions.append(FinancialRecord.category == filters.category)
    if filters.date_from is not None:
        conditions.append(FinancialRecord.entry_date >= filters.date_from)
    if filters.date_to is not None:
        conditions.append(FinancialRecord.entry_date <= filters.date_to)
    where_clause = and_(*conditions)

    total = db.execute(
        select(func.count()).select_from(FinancialRecord).where(where_clause)
    ).scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        select(FinancialRecord)
        .where(where_clause)
        .order_by(FinancialRecord.entry_date.desc(), FinancialRecord.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = db.execute(stmt).scalars().all()
    return list(rows), int(total)


def get_record(db: Session, record_id: int) -> FinancialRecord | None:
    return db.execute(_base_select().where(FinancialRecord.id == record_id)).scalar_one_or_none()


def create_record(db: Session, data: FinancialRecordCreate, created_by_id: int | None) -> FinancialRecord:
    rec = FinancialRecord(
        amount=Decimal(data.amount).quantize(Decimal("0.01")),
        type=data.type,
        category=data.category.strip(),
        entry_date=data.entry_date,
        notes=data.notes,
        created_by_id=created_by_id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def update_record(db: Session, record: FinancialRecord, data: FinancialRecordUpdate) -> FinancialRecord:
    if data.amount is not None:
        record.amount = Decimal(data.amount).quantize(Decimal("0.01"))
    if data.type is not None:
        record.type = data.type
    if data.category is not None:
        record.category = data.category.strip()
    if data.entry_date is not None:
        record.entry_date = data.entry_date
    if data.notes is not None:
        record.notes = data.notes
    db.commit()
    db.refresh(record)
    return record


def soft_delete_record(db: Session, record: FinancialRecord) -> None:
    record.is_deleted = True
    db.commit()
