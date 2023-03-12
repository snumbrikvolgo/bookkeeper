"""
Тесты GUI для главного окна
"""

from pytestqt.qt_compat import qt_api

from bookkeeper.view.main_window import MainWindow
from bookkeeper.view.tables import BudgetTable, ExpensesTable
from bookkeeper.view.edits import NewExpense

modifier = lambda pk, val1, val2: None
pk_to_name = lambda pk: ""
deleter = lambda pks: None
cats_edit_show = lambda: None
adder = lambda amount, name, comment: None
    

def test_create_window(qtbot):
    budget_table = BudgetTable(budget=[], bdg_modifier=modifier)
    new_expense = NewExpense([], cats_edit_show, adder)
    expenses_table = ExpensesTable([], deleter, modifier, pk_to_name)
    window = MainWindow(budget_table, new_expense, expenses_table)
    qtbot.addWidget(window)
    assert window.budget_table == budget_table
    assert window.new_expense == new_expense
    assert window.expenses_table == expenses_table

def test_close_event(qtbot):
        budget_table = BudgetTable(budget=[], bdg_modifier=modifier)
        new_expense = NewExpense([], cats_edit_show, adder)
        expenses_table = ExpensesTable([], deleter, modifier, pk_to_name)
        window = MainWindow(budget_table, new_expense, expenses_table)
        qtbot.addWidget(window)
        assert window.close() == True