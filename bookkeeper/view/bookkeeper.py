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
        
    def modify_exp(self, pk, attr, value, old_val):
        print(pk, attr, value, old_val)
        exp = self.expenses_rep.get(pk)
        error_str = ''
        try:
            if attr == "category":
                value = value.lower()
                if value not in [c.name for c in self.categories]:
                    # self.view.set_expenses(self.expenses)
                    error_str=f'Категории {value} не существует'
                    raise ValueError(f'Категории {value} не существует')
                value = self.category_rep.get_all(where={'name':value})[0].name
            elif attr == "amount":
                if int(value) <= 0:
                    self.view.set_expenses_list(self.expenses)
                    error_str=f'Стоимость покупки должна быть'\
                                +'целым положительным числом'

                    raise ValueError(f'Стоимость покупки должна быть'\
                                +'целым положительным числом')
            elif attr == "expense_date":
                try:
                    value = datetime.fromisoformat(value).isoformat(
                                                sep=' ', timespec='seconds')
                except ValueError:
                    self.view.set_expenses_list(self.expenses)
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

    def delete_exp(self, exps_pk: list[int]):
        if len(exps_pk) == 0:
            raise ValueError(f'Выберите расходы')
        for pk in exps_pk:
            self.expenses_rep.delete(pk)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)


