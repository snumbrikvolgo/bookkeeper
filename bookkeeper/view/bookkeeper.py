from datetime import datetime

from bookkeeper.view.view import AbstractView
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget

class Bookkeeper:
    def __init__(self,
                 view: AbstractView,
                 repository: type):
        
        self.view = view
        self.category_rep = repository[Category](
                            db_file="database/bookkeeper.db",
                            cls=Category)

        self.expenses_rep = repository[Expense](
                            db_file="database/bookkeeper.db",
                            cls=Expense)
        self.budget_rep = repository[Budget](
                            db_file="database/bookkeeper.db",
                            cls=Budget)
        self.categories = self.category_rep.get_all()
        self.expenses = self.expenses_rep.get_all()
        self.budget = self.budget_rep.get_all()

        self.view.set_category_list(self.categories)
        self.view.set_expenses_list(self.expenses)
        self.view.set_budget_list(self.budget)

        self.view.register_cat_adder(self.add_cat)
        self.view.register_cat_modifier(self.modify_cat)
        self.view.register_cat_deleter(self.delete_cat)

        self.view.register_exp_adder(self.add_exp)
        self.view.register_exp_modifier(self.modify_exp)
        self.view.register_exp_deleter(self.delete_exp)

        self.view.register_bdg_modifier(self.modify_bdg)

    def run(self):
        self.view.show_main_window()
    
    def add_cat(self, name, parent):
        if name in [c.name for c in self.categories]:
            raise ValueError(f'Категория {name} уже существует')
        if parent is not None:
            if parent not in [c.name for c in self.categories]:
                raise ValueError(f'Категории {parent} не существует')
            parent_pk = self.category_rep.get_all(where={'name':parent})[0].pk
        else:
            parent_pk = None
        cat = Category(name, parent_pk)
        self.category_rep.add(cat)
        self.categories.append(cat)
        self.view.set_category_list(self.categories)
        
    def modify_cat(self, cat: Category) -> None:
        if cat not in [c.name for c in self.categories]:
            raise ValueError(f'Категории {cat.name} не существует')
        self.category_rep.update(cat)
        self.view.set_category_list(self.categories)

    def delete_cat(self, cat):
        children = self.category_rep.get_all(where={'parent':cat.pk})
        self.category_rep.delete(cat.pk)
        for exp in self.expenses_rep.get_all(where={'category':cat.name}):
                self.expenses_rep.delete(exp.pk)
        for child in children:
            self.category_rep.delete(child.pk)
            for exp in self.expenses_rep.get_all(where={'category':child.name}):
                self.expenses_rep.delete(exp.pk)
        self.categories = self.category_rep.get_all()
        self.expenses = self.expenses_rep.get_all()

        self.view.set_category_list(self.categories)
        self.view.set_expenses_list(self.expenses)

    def add_exp(self, amount: str, category: str, comment: str):
        amount = int(amount)
        if  (amount <= 0):
            raise ValueError(f'Стоимость покупки должна быть'\
                             +'целым положительным числом')
        exp = Expense(amount=amount, category=category, comment=comment)
        self.expenses_rep.add(exp)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        self.update_budgets()

    def modify_exp(self, pk, attr, value, old_val):
        print(pk, attr, value, old_val)
        exp = self.expenses_rep.get(pk)
        error_str = ''
        try:
            if attr == "category":
                value = value.lower()
                if value not in [c.name for c in self.categories]:
                    error_str=f'Категории {value} не существует'
                    raise ValueError(f'Категории {value} не существует')
                value = self.category_rep.get_all(where={'name':value})[0].name
            elif attr == "amount":
                if int(value) <= 0:
                    error_str=f'Стоимость покупки должна быть'\
                                +'целым положительным числом'

                    raise ValueError(f'Стоимость покупки должна быть'\
                                +'целым положительным числом')
            elif attr == "expense_date":
                try:
                    value = datetime.fromisoformat(value).isoformat(
                                                sep=' ', timespec='seconds')
                except ValueError:
                    error_str=f'Неправильный формат даты'
                    raise ValueError(error_str)
            setattr(exp, attr, value)
        except ValueError:
            self.view.set_expenses_list(self.expenses)
            raise ValueError(error_str)
        else:
            setattr(exp, attr, old_val)
        self.expenses_rep.update(exp)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        self.update_budgets()

    def delete_exp(self, exps_pk: list[int]):
        for pk in exps_pk:
            self.expenses_rep.delete(pk)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        self.update_budgets()

    def update_budgets(self):
        for budget in self.budget_rep.get_all():
            budget.update_spent(self.expenses_rep)
            self.budget_rep.update(budget)
        self.budgets = self.budget_rep.get_all()
        self.view.set_budget_list(self.budgets)

    def modify_bdg(self, pk: int | None, new_limit: str, period: str):
        if new_limit == "":
            if pk is not None:
                self.budget_rep.delete(pk)
            self.update_budgets()
            return
        try:
            new_limit = int(new_limit)
        except ValueError:
            self.update_budgets()
            raise ValueError(f'Стоимость покупки должна быть'\
                             +'целым положительным числом')
        if new_limit < 0:
            self.update_budgets()
            raise ValueError(f'Стоимость покупки должна быть'\
                             +'целым положительным числом')
        if pk is None:
            budget = Budget(limitation=new_limit, period=period)
            self.budget_rep.add(budget)
        else:
            budget = self.budget_rep.get(pk)
            budget.limitation = new_limit
            self.budget_rep.update(budget)
        self.update_budgets()

