import sys
from typing import Protocol
from collections.abc import Callable
from PySide6 import QtWidgets

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.view.main_window import MainWindow
from bookkeeper.view.edits import NewExpense
from bookkeeper.view.tables import ExpensesTable, BudgetTable
from bookkeeper.view.edits import CategoryEditWindow

class AbstractView(Protocol):

    def show_main_window() -> None:
        pass
    def set_category_list(cats : list[Category]) -> None:
        pass
    def set_expenses_list(exps : list[Expense]) -> None:
        pass
    def set_budget_list(buds: list[Budget]) -> None:
        pass

    def register_cat_modifier(handler: Callable[[Category], None]):
        pass
    def register_cat_deleter(handler: Callable[[Category], None]):
        pass
    def register_cat_adder(handler: Callable[[Category], None]):
        pass

    def register_exp_modifier(handler: Callable[[Expense], None]):
        pass
    def register_exp_deleter(handler: Callable[[Expense], None]):
        pass
    def register_exp_adder(handler: Callable[[Expense], None]):
        pass


def handle_error(widget, handler):
    def inner(*args, **kwargs):
        try:
            handler(*args, **kwargs)
        except ValueError as ex:
            QtWidgets.QMessageBox.critical(widget, 'Ошибка', str(ex))
    return inner

class View:

    categories: list[Category] = []
    expenses: list[Expense] = []
    budget: list[Budget] = []

    main_window: MainWindow
    budget_table: BudgetTable
    new_expense: NewExpense
    expenses_table: ExpensesTable
    cats_edit_window: CategoryEditWindow

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        #self.app.setQuitOnLastWindowClosed(False)
        self.app.setStyle("Fusion")
        self.category_edit_window()
        self.budget_table = BudgetTable(self.budget)
        self.new_expense = NewExpense(self.categories,\
                                       self.show_category_edit_window,
                                       self.add_expense,\
                                    )
        self.expenses_table = ExpensesTable(self.expenses, self.delete_expense, self.modify_expense)
        self.main_window = MainWindow(self.budget_table, 
                                    self.new_expense, 
                                      self.expenses_table)
        self.main_window.resize(800, 800)
        
    def show_main_window(self):
        self.main_window.show()
        # print("run app")
        print(f"Application ends with exit status {self.app.exec()}")
        sys.exit()
    
    def category_edit_window(self):
        self.cats_edit_window = CategoryEditWindow(self.categories, 
                                                     self.add_category,
                                                     self.delete_category,
                                                     self.modify_category)
        self.cats_edit_window.setWindowTitle("Редактирование категорий")
        self.cats_edit_window.resize(600, 600)

    def show_category_edit_window(self):
        self.category_edit_window()
        self.cats_edit_window.show()

    def set_category_list(self, cats: list[Category]) -> None:
        self.categories = cats
        self.new_expense.set_categories(self.categories)
        self.cats_edit_window.set_categories(self.categories)

    def set_expenses_list(self, exps: list[Expense]) -> None:
        self.expenses = exps
        self.expenses_table.set_expenses(self.expenses)

    def set_budget_list(self, buds: list[Budget]) -> None:
        self.budget = buds
        self.budget_table.set_budget(self.budget)

    def register_cat_modifier(self, handler: Callable[[Category], None]):
        self.cat_modifier = handle_error(self.main_window, handler)
    def register_cat_deleter(self, handler: Callable[[Category], None]):
        self.cat_deleter = handle_error(self.main_window, handler)
    def register_cat_adder(self, handler):
        self.cat_adder = handle_error(self.main_window, handler)

    def register_exp_modifier(self, handler):
        self.exp_modifier = handle_error(self.main_window, handler)    
    def register_exp_deleter(self, handler):
        self.exp_deleter = handle_error(self.main_window, handler)    
    def register_exp_adder(self, handler):
        self.exp_adder = handle_error(self.main_window, handler)    


    def add_category(self, name, parent):
        self.cat_adder(name, parent)
        # try:
        #     self.cat_adder(name, parent)
        # except ValidationError as ex:
        #     QMessageBox.critical(self, 'Ошибка', str(ex))
    def delete_category(self, name):
        cat = [c for c in self.categories if c.name == name][0]
        # del_subcats, del_expenses = self.ask_del_cat()
        # self.cat_deleter(cat, del_subcats, del_expenses)
        self.cat_deleter(cat)

    def modify_category(self, cat: Category):
        self.cat_modifier(cat)

    def add_expense(self, amount, category, comment):
        self.exp_adder(amount, category, comment)
    def delete_expense(self):
        pass
    def modify_expense(self):
        pass