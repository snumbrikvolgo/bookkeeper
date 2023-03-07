from PySide6 import QtWidgets
from bookkeeper.view.tables import ExpensesTable, BudgetTable
from bookkeeper.view.edits import NewExpense


class MainWindow(QtWidgets.QWidget):
    def __init__(self, budget_table: BudgetTable,
                       new_expense: NewExpense,
                       expenses_table: ExpensesTable,
                       *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.setWindowTitle("The Bookkeeper App")
        self.expenses_table = expenses_table
        self.vbox.addWidget(self.expenses_table, stretch=8)
        self.new_expense = new_expense
        self.vbox.addWidget(self.new_expense, stretch=3)
        self.budget_table = budget_table
        self.vbox.addWidget(self.budget_table, stretch=6)
        self.setLayout(self.vbox)