"""
Виджет главного окна
"""
from PySide6 import QtWidgets
from bookkeeper.view.tables import ExpensesTable, BudgetTable
from bookkeeper.view.edits import NewExpense
# pylint: disable=too-few-public-methods
# pylint: disable=c-extension-no-member)


class MainWindow(QtWidgets.QWidget):
    """
    Класс виджета главного окна
    """
    def __init__(self, budget_table: BudgetTable,  # type: ignore
                 new_expense: NewExpense,
                 expenses_table: ExpensesTable,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.setWindowTitle("The Bookkeeper App")
        self.expenses_table = expenses_table
        self.vbox.addWidget(self.expenses_table, stretch=6)
        self.new_expense = new_expense
        self.vbox.addWidget(self.new_expense, stretch=1)
        self.budget_table = budget_table
        self.vbox.addWidget(self.budget_table, stretch=3)
        self.setLayout(self.vbox)
