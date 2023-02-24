"""
Модель бюджета
"""
from dataclasses import dataclass


@dataclass(slots=True)
class Budget:
    """
    Строка бюджета за сколько-то дней за какую-то категорию расхода
    period - срок в днях
    category - id категории расходов
    amount - сумма
    pk - id записи в базе данных

    """
    amount: int
    category: int
    period: int
    pk: int = 0
