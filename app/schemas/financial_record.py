from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.financial_record import EntryType


class FinancialRecordBase(BaseModel):
    amount: Decimal = Field(gt=0)
    type: EntryType
    category: str = Field(min_length=1, max_length=100)
    entry_date: date
    notes: str | None = Field(default=None, max_length=5000)


class FinancialRecordCreate(FinancialRecordBase):
    pass


class FinancialRecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    type: EntryType | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    entry_date: date | None = None
    notes: str | None = Field(default=None, max_length=5000)


class FinancialRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    type: EntryType
    category: str
    entry_date: date
    notes: str | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime


class FinancialRecordFilter(BaseModel):
    type: EntryType | None = None
    category: str | None = Field(default=None, max_length=100)
    date_from: date | None = None
    date_to: date | None = None


class PaginatedRecords(BaseModel):
    items: list[FinancialRecordOut]
    total: int
    page: int
    page_size: int
