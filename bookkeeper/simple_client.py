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

while True:
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
        else:
            try:
                cat = cat_repo.get_all({'name': names[1]})[0]
            except IndexError:
                print(f'категория {names[1]} не найдена')
                continue
            bud = Budget(int(names[0]), cat.pk, int(names[2]))
            bud_repo.add(bud)
            print(bud)

