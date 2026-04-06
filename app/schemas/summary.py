from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.financial_record import EntryType


class CategoryTotal(BaseModel):
    category: str
    total_income: Decimal
    total_expense: Decimal
    net: Decimal


class PeriodTrend(BaseModel):
    period_start: date
    period_label: str
    income: Decimal
    expense: Decimal
    net: Decimal


class RecentActivityItem(BaseModel):
    id: int
    amount: Decimal
    type: EntryType
    category: str
    entry_date: date
    notes: str | None = None


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    category_totals: list[CategoryTotal]
    recent_activity: list[RecentActivityItem] = Field(default_factory=list)
