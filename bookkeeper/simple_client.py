"""
Простой тестовый скрипт для терминала
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.utils import read_tree

cat_repo = MemoryRepository[Category]()
exp_repo = MemoryRepository[Expense]()
bud_repo = MemoryRepository[Budget]()

cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

Category.create_from_tree(read_tree(cats), cat_repo)
budget = Budget(period="day", limitation=1000, spent=0)
bud_repo.add(budget)
budget = Budget(period="week", limitation=7000, spent=0)
bud_repo.add(budget)
budget = Budget(period="month", limitation=30000, spent=0)
bud_repo.add(budget)

while True:  # noqa
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd == 'бюджет':
        print(*bud_repo.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        names = cmd.split(maxsplit=-1)
        # amount, name = cmd.split(maxsplit=1)
        if len(names) == 2:
            try:
                cat = cat_repo.get_all({'name': names[1]})[0]
            except IndexError:
                print(f'категория {names[1]} не найдена')
                continue
            exp = Expense(int(names[0]), cat.pk)
            exp_repo.add(exp)
            print(exp)
            for budget in bud_repo.get_all():
                budget.update_spent(exp_repo)
                bud_repo.update(budget)
        else:
            try:
                cat = cat_repo.get_all({'name': names[1]})[0]
            except IndexError:
                print(f'категория {names[1]} не найдена')
                continue
