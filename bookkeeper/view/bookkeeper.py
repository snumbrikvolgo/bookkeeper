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
        
    def modify_cat(self, cat: Category) -> None:
        if cat not in [c.name for c in self.categories]:
            raise ValueError(f'Категории {cat.name} не существует')
        self.category_rep.update(cat)
        self.view.set_category_list(self.categories)

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
        
    def delete_cat(self, cat):
        children = self.category_rep.get_all(where={'parent':cat.pk})
        self.category_rep.delete(cat.pk)
        for child in children:
            self.category_rep.delete(child.pk)
        self.categories = self.category_rep.get_all()
        self.view.set_category_list(self.categories)
        
    def modify_exp(self):
        pass
    
    def add_exp(self, amount, category, comment):
        exp = Expense(amount=amount, category=category, comment=comment)
        self.expenses_rep.add(exp)
        self.expenses = self.expenses_rep.get_all()
        self.view.set_expenses_list(self.expenses)
        
    def delete_exp(self, name, parent):
        pass


