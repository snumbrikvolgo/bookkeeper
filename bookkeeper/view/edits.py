"""
Редактирования категории и внесение новой затраты
"""
from collections.abc import Callable
from PySide6 import QtWidgets
from bookkeeper.view.labels import GroupLabelCenter, LabeledComboBoxInput, LabeledLineInput
from bookkeeper.models.category import Category
# pylint: disable = no-name-in-module
# # pylint: disable=c-extension-no-member
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes


class CategoryEditWindow(QtWidgets.QWidget):
    """
    Виджет окна редактирования категории
    """
    def __init__(self, cats: list[Category],  # type: ignore
                 cat_adder: Callable[[], None], cat_deleter: Callable[[], None],
                 cat_modifier: Callable[[], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = QtWidgets.QGridLayout()
        self.label = GroupLabelCenter("<b>Список категорий</b>")
        self.grid.addWidget(self.label, 0, 0, 1, 2)

        self.cats_tree = QtWidgets.QTreeWidget()
        self.cats_tree.setHeaderLabel("")
        self.grid.addWidget(self.cats_tree, 1, 0, 1, 2)
        self.cats_tree.itemClicked.connect(self.once_clicked)  # type: ignore

        self.label = GroupLabelCenter("<b>Удаление категории</b>")
        self.grid.addWidget(self.label, 2, 0, 1, 2)

        self.cat_del = LabeledComboBoxInput("Категория", [])
        self.grid.addWidget(self.cat_del, 3, 0, 1, 1)

        # self.calendar = QtWidgets.QCalendarWidget()
        # self.grid.addWidget(self.calendar)

        self.cat_del_button = QtWidgets.QPushButton('Удалить')
        self.cat_del_button.clicked.connect(self.delete_category)  # type: ignore
        self.grid.addWidget(self.cat_del_button, 3, 1, 1, 1)

        self.label = GroupLabelCenter("<b>Добавление категории</b>")
        self.grid.addWidget(self.label, 4, 0, 1, 2)

        self.cat_add_parent = LabeledComboBoxInput("Родитель", [])
        self.grid.addWidget(self.cat_add_parent, 5, 0, 1, 1)

        self.cat_add_name = LabeledLineInput("Название", "Новая категория")
        self.grid.addWidget(self.cat_add_name, 6, 0, 1, 1)

        self.cat_add_button = QtWidgets.QPushButton('Добавить')
        self.cat_add_button.clicked.connect(self.add_category)  # type: ignore
        self.grid.addWidget(self.cat_add_button, 6, 1, 1, 1)

        self.setLayout(self.grid)
        self.cat_adder = cat_adder
        self.cat_deleter = cat_deleter
        self.cat_modifier = cat_modifier

        self.set_categories(cats)

    def once_clicked(self, item, column: int) -> None:  # type: ignore
        """
        Реакция на одно нажатие -- установка в списке категорий
        """
        clicked_cat_name = item.text(column)
        self.cat_del.set_text(clicked_cat_name)
        self.cat_add_parent.set_text(clicked_cat_name)

    def set_categories(self, cats: list[Category]) -> None:
        """
        Установка категории
        """
        self.categories = cats
        self.cat_names = [c.name for c in cats]
        top_items = self.find_children()
        self.cats_tree.clear()
        self.cats_tree.insertTopLevelItems(0, top_items)
        self.cat_del.set_items(self.cat_names)
        self.cat_names.append("Нет в списке")
        self.cat_add_parent.set_items(self.cat_names)

    def delete_category(self) -> None:
        """
        Удаление категории
        """
        name = self.cat_del.text()
        self.cat_deleter(self.cat_del.text())  # type: ignore
        print(f"Категория {name} удалена")
        self.cat_del.clear()

    def add_category(self) -> None:
        """
        Добавление категории
        """
        if self.cat_add_parent.text() == "Нет в списке":
            self.cat_adder(self.cat_add_name.text(), None)  # type: ignore
            print(f"Категория '{self.cat_add_name.text()}' добавлена")
        else:
            self.cat_adder(self.cat_add_name.text(), self.cat_add_parent.text())  # type: ignore
            print(f"Подкатегория '{self.cat_add_name.text()}' категории "
                  + f"'{self.cat_add_parent.text()}' добавлена")
        self.cat_add_name.clear()
        self.cat_add_parent.clear()

    def find_children(self, parent_pk: int | None = None) -> list[QtWidgets.QTreeWidgetItem]:
        """
        Найти дочерние подкатегории
        """
        items = []
        children = [c for c in self.categories if c.parent == parent_pk]
        for child in children:
            item = QtWidgets.QTreeWidgetItem([child.name])
            item.addChildren(self.find_children(parent_pk=child.pk))
            items.append(item)
        return items

class NewExpense(QtWidgets.QGroupBox):
    """
    Виджет добавление расхода и категории
    """
    def __init__(self, cats: list[Category],  # type: ignore
                 show_category_edit_window: Callable[[], None], exp_adder: Callable[[], None],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = cats
        self.show_category_edit_window = show_category_edit_window
        self.exp_adder = exp_adder
        self.cat_names = [c.name for c in cats]

        self.grid = QtWidgets.QGridLayout()
        self.label = GroupLabelCenter("<b>Новая трата</b>")
        self.grid.addWidget(self.label,0,0,1,5)

        self.amount_input = LabeledLineInput("Сумма", "0")
        self.grid.addWidget(self.amount_input,1,0,1,2)

        self.comment_input = LabeledLineInput("Комментарий", "")
        self.grid.addWidget(self.comment_input,2,0,1,5)

        self.category_input = LabeledComboBoxInput("Категория", self.cat_names)
        self.grid.addWidget(self.category_input,3,0,1,2)

        self.cats_edit_button = QtWidgets.QPushButton('Редактировать')
        self.cats_edit_button.clicked.connect(self.show_category_edit_window)  # type: ignore
        self.grid.addWidget(self.cats_edit_button,3,2,1,3)

        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self.submit)  # type: ignore
        self.grid.addWidget(self.submit_button,4,0,1,5)
        self.setLayout(self.grid)

    def submit(self) -> None:
        """
        Добавление расхода
        """
        self.exp_adder(self.amount_input.text(),  # type: ignore
                       self.category_input.text(),
                       self.comment_input.text())
        print(f"Новая трата в категории {self.category_input.text()}"+\
              " на сумму {self.amount_input.text()} добавлена")
        self.amount_input.clear()
        self.category_input.clear()

    # def edit_categories(self) -> None:
    #     self.win = CategoryEditWindow(self.cat_repo)
    #     self.win.resize(400, 400)
    #     self.win.show()

    def set_categories(self, cats: list[Category]) -> None:
        """
        Установление категории
        """
        self.categories = cats
        self.cat_names = [c.name for c in cats]
        self.category_input.set_items(self.cat_names)
