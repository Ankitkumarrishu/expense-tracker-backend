from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import RecordsReader, RecordsWriter
from app.database import get_db
from app.models.financial_record import EntryType
from app.schemas.financial_record import (
    FinancialRecordCreate,
    FinancialRecordFilter,
    FinancialRecordOut,
    FinancialRecordUpdate,
    PaginatedRecords,
)
from app.services import record_service

router = APIRouter()


@router.get("", response_model=PaginatedRecords)
def list_records(
    reader: RecordsReader,
    db: Annotated[Session, Depends(get_db)],
    type: Annotated[EntryType | None, Query()] = None,
    category: Annotated[str | None, Query(max_length=100)] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be on or before date_to",
        )
    filters = FinancialRecordFilter(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )
    rows, total = record_service.list_records(db, filters, page, page_size)
    return PaginatedRecords(
        items=[FinancialRecordOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=FinancialRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    writer: RecordsWriter,
    db: Annotated[Session, Depends(get_db)],
    body: FinancialRecordCreate,
):
    rec = record_service.create_record(db, body, created_by_id=writer.id)
    return rec


@router.get("/{record_id}", response_model=FinancialRecordOut)
def get_record(reader: RecordsReader, db: Annotated[Session, Depends(get_db)], record_id: int):
    rec = record_service.get_record(db, record_id)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return rec


@router.patch("/{record_id}", response_model=FinancialRecordOut)
def update_record(
    writer: RecordsWriter,
    db: Annotated[Session, Depends(get_db)],
    record_id: int,
    body: FinancialRecordUpdate,
):
    rec = record_service.get_record(db, record_id)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record_service.update_record(db, rec, body)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(writer: RecordsWriter, db: Annotated[Session, Depends(get_db)], record_id: int):
    rec = record_service.get_record(db, record_id)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    record_service.soft_delete_record(db, rec)
    return None
