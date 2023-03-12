"""
Описан класс презентера
"""
from datetime import datetime
from bookkeeper.view.view import AbstractView
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget


class Bookkeeper:
    """
    Класс презентера
    """
    def __init__(self,
                 view: AbstractView,
                 repository: type):
        self.view = view
        self.category_rep = repository[Category](  # type: ignore
                            db_file="database/bookkeeper.db",
                            cls=Category)

        self.expenses_rep = repository[Expense](  # type: ignore
                            db_file="database/bookkeeper.db",
                            cls=Expense)
        self.budget_rep = repository[Budget](  # type: ignore
                            db_file="database/bookkeeper.db",
                            cls=Budget)
        self.categories = self.category_rep.get_all()
        self.expenses = self.expenses_rep.get_all()
        self.budget = self.budget_rep.get_all()
        self.update_budget()
        self.view.set_category_list(self.categories)
        self.view.set_expenses_list(self.expenses)
        self.view.set_budget_list(self.budget)

        self.view.register_cat_adder(self.add_cat)  # type: ignore
        self.view.register_cat_modifier(self.modify_cat)  # type: ignore
        self.view.register_cat_deleter(self.delete_cat)  # type: ignore

        self.view.register_exp_adder(self.add_exp)  # type: ignore
        self.view.register_exp_modifier(self.modify_exp)  # type: ignore
        self.view.register_exp_deleter(self.delete_exp)  # type: ignore

        self.view.register_bdg_modifier(self.modify_bdg)  # type: ignore

    def run(self) -> None:
        """
        Запуск приложения
        """
        self.view.show_main_window()

    def add_cat(self, name: str, parent: str) -> None:
        """
        Добавить категорию
        """
        if name in [c.name for c in self.categories]:
            raise ValueError(f'Категория {name} уже существует')
        if parent is not None:
            if parent not in [c.name for c in self.categories]:
                raise ValueError(f'Категории {parent} не существует')
            parent_pk = self.category_rep.get_all(where={'name': parent})[0].pk
        else:
            parent_pk = None
        cat = Category(name, parent_pk)
        self.category_rep.add(cat)
        self.categories.append(cat)
        self.view.set_category_list(self.categories)

    def modify_cat(self, cat: Category) -> None:
        """
        Изменить категорию
        """
        if cat not in [c.name for c in self.categories]:
            raise ValueError(f'Категории {cat.name} не существует')
        self.category_rep.update(cat)
        self.view.set_category_list(self.categories)

    def delete_cat(self, cat: Category) -> None:
        """
        Удалить категорию
        """
        children = self.category_rep.get_all(where={'parent': cat.pk})
        self.category_rep.delete(cat.pk)
        for exp in self.expenses_rep.get_all(where={'category': cat.pk}):
            self.expenses_rep.delete(exp.pk)
        for child in children:
            self.category_rep.delete(child.pk)
            for exp in self.expenses_rep.get_all(where={'category': child.pk}):
                self.expenses_rep.delete(exp.pk)
        self.categories = self.category_rep.get_all()
        self.expenses = self.expenses_rep.get_all()

        self.view.set_category_list(self.categories)
        self.view.set_expenses_list(self.expenses)

    def add_exp(self, amount: str, category: str, comment: str) -> None:
        """
        Добавить расход
        """
        int_amount = int(amount)
        if int_amount <= 0:
            raise ValueError('Стоимость покупки должна быть' +
                             'целым положительным числом')
        cat = self.category_rep.get_all(where={"name": category})[0]
        exp = Expense(amount=int_amount, category=cat.pk, comment=comment)
        self.expenses_rep.add(exp)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        self.update_budget()

    def modify_exp(self, pk: int, attr: str, value: str) -> None:
        """
        Изменить расход
        """
        exp = self.expenses_rep.get(pk)
        error_str = ''
        try:
            if attr == "category":
                value = value.lower()
                if value not in [c.name for c in self.categories]:
                    error_str = f'Категории {value} не существует'
                    raise ValueError(f'Категории {value} не существует')
                value_int = self.category_rep.get_all(where={'name': value})[0].pk
                setattr(exp, attr, value_int)
            elif attr == "amount":
                if int(value) <= 0:
                    error_str = 'Стоимость покупки должна быть' +\
                                'целым положительным числом'

                    raise ValueError('Стоимость покупки должна быть' +
                                     'целым положительным числом')
                setattr(exp, attr, value)
            elif attr == "expense_date":
                try:
                    value = datetime.fromisoformat(value).isoformat(
                                                sep=' ', timespec='seconds')
                except ValueError as err:
                    error_str = 'Неправильный формат даты'
                    raise ValueError(error_str) from err
                setattr(exp, attr, value)
        except ValueError as err:
            self.view.set_expenses_list(self.expenses)
            raise ValueError(error_str) from err
        # else:
        #     setattr(exp, attr, old_val)
        self.expenses_rep.update(exp)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        self.update_budget()

    def delete_exp(self, exps_pk: list[int]) -> None:
        """
        Удалить расход
        """
        for pk in exps_pk:
            self.expenses_rep.delete(pk)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        self.update_budget()

    def update_budget(self) -> None:
        """
        Обновить бюджет по изменении расходов или при изменении вне программы
        """
        for budget in self.budget_rep.get_all():
            budget.update_spent(self.expenses_rep)
            self.budget_rep.update(budget)
        self.budget = self.budget_rep.get_all()
        self.view.set_budget_list(self.budget)

    def modify_bdg(self, pk: int | None, new_limit: str, period: str) -> None:
        """
        Обновить бюджет
        """
        if new_limit == "":
            if pk is not None:
                self.budget_rep.delete(pk)
            self.update_budget()
            return
        try:
            new_limit_int = int(new_limit)
        except ValueError as err:
            self.update_budget()
            raise ValueError('Стоимость покупки должна быть' +
                             ' целым положительным числом') from err
        if new_limit_int < 0:
            self.update_budget()
            raise ValueError('Стоимость покупки должна быть'
                             + ' целым положительным числом')
        if pk is None:
            budget = Budget(limitation=new_limit_int, period=period)
            self.budget_rep.add(budget)
        else:
            budget = self.budget_rep.get(pk)
            budget.limitation = new_limit_int
            self.budget_rep.update(budget)
        self.update_budget()
