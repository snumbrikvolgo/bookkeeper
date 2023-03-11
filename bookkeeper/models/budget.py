"""
Модель бюджета
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense

@dataclass(slots=True)
class Budget:
    """
    Строка бюджета за сколько-то дней за какую-то категорию расхода
    limitation - ограничение на бюджет
    period - день/неделя/месяц
    spent - сумма потраченная
    pk - id записи в базе данных

    """
    limitation: int
    period: str
    spent: str = 0
    pk: str = 0

    def __init__(self, limitation: int, period: str, 
                       spent: str = 0, pk: str = 0):
        if period not in ["day", "week", "month"]:
            raise ValueError(f'unknown period "{period}" for budget'
                             + 'should be "day", "week" or "month"')
        self.limitation = limitation
        self.period = period
        self.spent = spent
        self.pk = pk

    def wrap_format_get_all(self, date_mask: str):
        values = [f"%{v}%" for v in {"expense_date":date_mask}.values()]
        where = dict(zip({"expense_date":date_mask}.keys(), values))
        return where
    
    def update_spent(self, exp_repo: AbstractRepository[Expense]) -> None:
        date = datetime.now().isoformat()[:10]
        if self.period.lower() == "day":
            date_mask = f"{date}"
            where=self.wrap_format_get_all(date_mask)
            period_exps = exp_repo.get_all(where=where, operator="LIKE")
        elif self.period.lower() == "week":
            weekday_now = datetime.now().weekday()
            day_now = datetime.fromisoformat(date)
            first_week_day = day_now - timedelta(days=weekday_now)
            period_exps = []
            for i in range(7):
                weekday = first_week_day + timedelta(days=i)
                date_mask = f"{weekday.isoformat()[:10]}"
                where=self.wrap_format_get_all(date_mask)
                period_exps += exp_repo.get_all(where=where, operator="LIKE")
        elif self.period.lower() == "month":
            date_mask = f"{date[:7]}-"
            where=self.wrap_format_get_all(date_mask)
            period_exps = exp_repo.get_all(where=where, operator="LIKE")
        self.spent = sum([int(exp.amount) for exp in period_exps])