from calendar import month_name
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.financial_record import EntryType, FinancialRecord
from app.models.user import UserRole
from app.schemas.summary import CategoryTotal, DashboardSummary, PeriodTrend, RecentActivityItem


def _non_deleted_filter():
    return FinancialRecord.is_deleted.is_(False)


def _date_clause(date_from: date | None, date_to: date | None):
    parts = [_non_deleted_filter()]
    if date_from is not None:
        parts.append(FinancialRecord.entry_date >= date_from)
    if date_to is not None:
        parts.append(FinancialRecord.entry_date <= date_to)
    return and_(*parts)


def build_dashboard_summary(
    db: Session,
    *,
    viewer_role: UserRole,
    date_from: date | None = None,
    date_to: date | None = None,
    recent_limit: int = 10,
) -> DashboardSummary:
    clause = _date_clause(date_from, date_to)

    income_stmt = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
        and_(clause, FinancialRecord.type == EntryType.INCOME)
    )
    expense_stmt = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
        and_(clause, FinancialRecord.type == EntryType.EXPENSE)
    )
    total_income = Decimal(db.execute(income_stmt).scalar_one())
    total_expense = Decimal(db.execute(expense_stmt).scalar_one())
    net = total_income - total_expense

    cat_stmt = (
        select(FinancialRecord.category, FinancialRecord.type, func.sum(FinancialRecord.amount))
        .where(clause)
        .group_by(FinancialRecord.category, FinancialRecord.type)
    )
    agg: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0")})
    for category, etype, total in db.execute(cat_stmt).all():
        key = "income" if etype == EntryType.INCOME else "expense"
        agg[category][key] = Decimal(total)

    category_totals = [
        CategoryTotal(
            category=c,
            total_income=v["income"],
            total_expense=v["expense"],
            net=v["income"] - v["expense"],
        )
        for c, v in sorted(agg.items(), key=lambda x: x[0].lower())
    ]

    recent: list[RecentActivityItem] = []
    if viewer_role in (UserRole.ANALYST, UserRole.ADMIN):
        recent_stmt = (
            select(FinancialRecord)
            .where(clause)
            .order_by(FinancialRecord.entry_date.desc(), FinancialRecord.id.desc())
            .limit(recent_limit)
        )
        for r in db.execute(recent_stmt).scalars().all():
            recent.append(
                RecentActivityItem(
                    id=r.id,
                    amount=r.amount,
                    type=r.type,
                    category=r.category,
                    entry_date=r.entry_date,
                    notes=r.notes,
                )
            )

    return DashboardSummary(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net,
        category_totals=category_totals,
        recent_activity=recent,
    )


def build_trends(
    db: Session,
    *,
    granularity: str,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[PeriodTrend]:
    clause = _date_clause(date_from, date_to)
    stmt = select(FinancialRecord).where(clause)
    records = db.execute(stmt).scalars().all()

    buckets: dict[date, dict[str, Decimal]] = defaultdict(
        lambda: {"income": Decimal("0"), "expense": Decimal("0")}
    )

    for r in records:
        if granularity == "week":
            start = r.entry_date - timedelta(days=r.entry_date.weekday())
            label = f"{start.isoformat()} week"
        else:
            start = r.entry_date.replace(day=1)
            label = f"{month_name[start.month]} {start.year}"

        b = buckets[start]
        if r.type == EntryType.INCOME:
            b["income"] += Decimal(r.amount)
        else:
            b["expense"] += Decimal(r.amount)

    out: list[PeriodTrend] = []
    for period_start in sorted(buckets.keys()):
        if granularity == "week":
            plabel = f"{period_start.isoformat()} week"
        else:
            plabel = f"{month_name[period_start.month]} {period_start.year}"
        inc = buckets[period_start]["income"]
        exp = buckets[period_start]["expense"]
        out.append(
            PeriodTrend(
                period_start=period_start,
                period_label=plabel,
                income=inc,
                expense=exp,
                net=inc - exp,
            )
        )
    return out
