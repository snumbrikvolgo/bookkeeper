from PySide6 import QtWidgets
from PySide6.QtCore import SignalInstance

from bookkeeper.view.labels import GroupLabel, LabeledComboBoxInput, LabeledLineInput
from bookkeeper.utils import read_tree
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.category import Category


cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

class CatsEditWindow(QtWidgets.QWidget):
    window_closed = SignalInstance()
    def __init__(self, cat_repo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabel("<b>Список категорий</b>")
        self.vbox.addWidget(self.label)
        self.cats_tree = QtWidgets.QTreeWidget()
        self.cats_tree.setColumnCount(1)

        self.cat_repo = cat_repo
        # Category.create_from_tree(read_tree(cats), self.cat_repo)
        top_items = self.find_children()
        self.cats_tree.insertTopLevelItems(0, top_items)
        self.vbox.addWidget(self.cats_tree)

        cat_names = []
        for cat in self.cat_repo.get_all():
            cat_names.append(cat.name)
        cat_names.append("Нет в списке")
        print('enter')
        self.parent_input = LabeledComboBoxInput("Чья подкатегория?", cat_names)
        self.vbox.addWidget(self.parent_input)

        self.category_input = LabeledLineInput("Название новой категории", "")
        self.vbox.addWidget(self.category_input)

        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self.submit)
        self.vbox.addWidget(self.submit_button)
        self.setLayout(self.vbox)

    # def closeEvent(self, event):
    #     print('close')
    #     self.window_closed.emit()
    #     event.accept()

    def find_children(self, parent_pk=None):
        items = []
        children = self.cat_repo.get_all(where={'parent':parent_pk})
        for child in children:
            item = QtWidgets.QTreeWidgetItem([child.name])
            item.addChildren(self.find_children(parent_pk=child.pk))
            items.append(item)
        return items
    
    def submit(self):
        print(f"Новая категория {self.category_input.text()} в раздел {self.parent_input.text()} добавлена")
        self.cat_repo.add(Category(self.category_input.text(), self.find_pk_by_name(self.parent_input.text())))
        print(self.cat_repo.get_all())
        self.parent_input.clear()
        self.category_input.clear()

    def find_pk_by_name(self, name):
        for item in self.cat_repo.get_all():
            if (item.name == name):
                return item.pk

class NewExpense(QtWidgets.QGroupBox):
    categories = [f"Категория {i}" for i in range(5)]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = QtWidgets.QGridLayout()
        self.label = GroupLabel("<b>Новая трата</b>")
        self.grid.addWidget(self.label,0,0,1,3)

        self.amount_input = LabeledLineInput("Сумма", "0")
        self.grid.addWidget(self.amount_input,1,0,1,2)

        self.cat_repo = MemoryRepository[Category]()
        Category.create_from_tree(read_tree(cats), self.cat_repo)
        cat_names = []
        for cat in self.cat_repo.get_all():
            cat_names.append(cat.name)
        # print(self.cat_repo.get_all())
        self.category_input = LabeledComboBoxInput("Категория", cat_names)
        self.grid.addWidget(self.category_input,2,0,1,2)

        self.cats_edit_button = QtWidgets.QPushButton('Редактировать')
        self.cats_edit_button.clicked.connect(self.cats_edit)
        self.grid.addWidget(self.cats_edit_button,2,2,1,1)

        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self.submit)
        self.grid.addWidget(self.submit_button,3,0,1,3)
        self.setLayout(self.grid)
    
    def submit(self):
        print(f"Новая трата в категории {self.category_input.text()} на сумму {self.amount_input.text()} добавлена")
        self.amount_input.clear()
        self.category_input.clear()
    
    def cats_edit(self):
        self.window = CatsEditWindow(self.cat_repo)
        self.window.resize(400, 400)
        self.window.show()
        # self.window.window_closed.connect(self.do_something)

    def do_something(self):
        print("You closed the second window!")