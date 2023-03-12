"""
Графический интерфейс приложения
"""
import sys
from typing import Protocol
from collections.abc import Callable
from PySide6 import QtWidgets
# pylint: disable=too-many-instance-attributes
# pylint: disable=c-extension-no-member

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.view.main_window import MainWindow
from bookkeeper.view.edits import NewExpense
from bookkeeper.view.tables import ExpensesTable, BudgetTable
from bookkeeper.view.edits import CategoryEditWindow


class AbstractView(Protocol):
    """
    Абстрактный интерфейс, позволяющий соединять модели и презентера
    """
    def show_main_window(self) -> None:
        """
        Показ виджета главного окна
        """
    def set_category_list(self, cats: list[Category]) -> None:
        """
        Отображение категорий
        """
    def set_expenses_list(self, exps: list[Expense]) -> None:
        """
        Отображение расходов
        """
    def set_budget_list(self, buds: list[Budget]) -> None:
        """
        Отображение бюджета
        """
    def register_cat_adder(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
    def register_cat_modifier(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
    def register_cat_deleter(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
    def register_exp_adder(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
    def register_exp_modifier(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
    def register_exp_deleter(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
    def register_bdg_modifier(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """


def handle_error(widget: QtWidgets.QWidget,
                 handler: Callable[[], None]) -> Callable[[], None]:
    """
    Показ ошибки в случае ошибки
    """
    def inner(*args: tuple[int, ...], **kwargs: dict[str, int]) -> None:
        try:
            handler(*args, **kwargs)
        except ValueError as exeption:
            QtWidgets.QMessageBox.critical(widget, 'Ошибка', str(exeption))
    return inner


class View:
    """
    Графический нтерфейс, позволяющий соединять модели и презентера
    """
    # pylint: disable=too-many-instance-attributes
    categories: list[Category] = []
    expenses: list[Expense] = []
    budget: list[Budget] = []
    main_window: MainWindow
    budget_table: BudgetTable
    new_expense: NewExpense
    expenses_table: ExpensesTable
    cats_edit_window: CategoryEditWindow
    cat_adder: Callable[[], None]
    cat_modifier: Callable[[], None]
    cat_deleter: Callable[[], None]
    exp_adder: Callable[[], None]
    exp_modifier: Callable[[], None]
    exp_deleter: Callable[[], None]
    bdg_modifier: Callable[[], None]

    def __init__(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)
        # self.app.setQuitOnLastWindowClosed(False)
        self.app.setStyle("Fusion")
        self.category_edit_window()
        self.budget_table = BudgetTable(self.budget, self.modify_budget)  # type: ignore
        self.new_expense = NewExpense(self.categories,
                                      self.show_category_edit_window,
                                      self.add_expense)  # type: ignore
        self.expenses_table = ExpensesTable(self.expenses,
                                            self.delete_expense,  # type: ignore
                                            self.modify_expense,  # type: ignore
                                            self.catpk_to_name)  # type: ignore
        self.main_window = MainWindow(self.budget_table,
                                      self.new_expense,
                                      self.expenses_table)
        self.main_window.resize(800, 800)

    def show_main_window(self) -> None:
        """
        Отображение главного окна
        """
        self.main_window.show()
        # print("run app")
        print(f"Application ends with exit status {self.app.exec()}")
        sys.exit()

    def category_edit_window(self) -> None:
        """
        Создание окна редактирования категорий
        """
        self.cats_edit_window = CategoryEditWindow(self.categories,
                                                   self.add_category,  # type: ignore
                                                   self.delete_category,  # type: ignore
                                                   self.modify_category)  # type: ignore
        self.cats_edit_window.setWindowTitle("Редактирование категорий")
        self.cats_edit_window.resize(600, 600)

    def show_category_edit_window(self) -> None:
        """
        Отображение окна редактирования категорий
        """
        self.category_edit_window()
        self.cats_edit_window.show()

    def set_category_list(self, cats: list[Category]) -> None:
        """
        Отображение категорий
        """
        self.categories = cats
        self.new_expense.set_categories(self.categories)
        self.cats_edit_window.set_categories(self.categories)

    def set_expenses_list(self, exps: list[Expense]) -> None:
        """
        Отображение расходов
        """
        self.expenses = exps
        self.expenses_table.set_expenses(self.expenses)

    def set_budget_list(self, buds: list[Budget]) -> None:
        """
        Отображение бюджета
        """
        self.budget = buds
        self.budget_table.set_budget(self.budget)

    def register_cat_adder(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.cat_adder = handle_error(self.main_window, handler)

    def register_cat_modifier(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.cat_modifier = handle_error(self.main_window, handler)

    def register_cat_deleter(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.cat_deleter = handle_error(self.main_window, handler)

    def register_exp_adder(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.exp_adder = handle_error(self.main_window, handler)

    def register_exp_modifier(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.exp_modifier = handle_error(self.main_window, handler)

    def register_exp_deleter(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.exp_deleter = handle_error(self.main_window, handler)

    def register_bdg_modifier(self, handler: Callable[[], None]) -> None:
        """
        Присоединение презентера
        """
        self.bdg_modifier = handle_error(self.main_window, handler)

    def add_category(self, name: str, parent: str) -> None:
        """
        Вызов у презентера
        """
        self.cat_adder(name, parent)  # type: ignore

        # try:
        #     self.cat_adder(name, parent)
        # except ValidationError as ex:
        #     QMessageBox.critical(self, 'Ошибка', str(ex))
    def modify_category(self, cat: Category) -> None:
        """
        Вызов у презентера
        """
        self.cat_modifier(cat)  # type: ignore

    def delete_category(self, name: str) -> None:
        """
        Вызов у презентера
        """
        cat = [c for c in self.categories if c.name == name][0]
        reply = QtWidgets.QMessageBox.question(self.main_window, 'Удаление категории',
                'Вы уверены, что хотите удалить категорию?')  # noqa: E128
        if reply == QtWidgets.QMessageBox.Yes:  # type: ignore
            self.cat_deleter(cat)  # type: ignore

    def add_expense(self, amount: str, category: str, comment: str) -> None:
        """
        Вызов у презентера
        """
        self.exp_adder(amount, category, comment)  # type: ignore

    def modify_expense(self, pk: int, attr: str, value: str, old_val: str) -> None:
        """
        Вызов у презентера
        """
        self.exp_modifier(pk, attr, value, old_val)  # type: ignore

    def delete_expense(self, exps_pk: list[int]) -> None:
        """
        Вызов у презентера
        """
        if len(exps_pk) == 0:
            QtWidgets.QMessageBox.critical(self.main_window, 'Ошибка',
                                           'Траты для удаления не выбраны.')
        else:
            reply = QtWidgets.QMessageBox.question(self.main_window, 'Удаление трат',
                    'Вы уверены, что хотите удалить все выбранные траты?')  # noqa: E128
            if reply == QtWidgets.QMessageBox.Yes:  # type: ignore
                self.exp_deleter(exps_pk)  # type: ignore

    def modify_budget(self, pk: int | None, new_limit: str, period: str) -> None:
        """
        Вызов у презентера
        """
        self.bdg_modifier(pk, new_limit, period)  # type: ignore

    def catpk_to_name(self, pk: int) -> str:
        name = [c.name for c in self.categories if int(c.pk) == int(pk)]
        if len(name):
            return str(name[0])
        return ""