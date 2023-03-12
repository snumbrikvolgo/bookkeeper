"""
Виджеты бюджета и расходов
"""
# pylint: disable = no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name
from collections.abc import Callable
from typing import Any, List
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from bookkeeper.view.labels import GroupLabelCenter
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget


class ExpensesTableWidget(QtWidgets.QTableWidget):
    """
    Таблица расходов
    """
    data: List[List[Any]] = []

    def __init__(self,  # type: ignore
                 *args, h_header_str: str = "", row_count: int = 50, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(4)
        self.setRowCount(row_count)
        self.headers = h_header_str.split()
        self.col_to_attr = {0: "expense_date", 1: "amount",
                            2: "category", 3: "comment"}
        self.setHorizontalHeaderLabels(self.headers)

        header = self.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)  # type: ignore
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)  # type: ignore
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)  # type: ignore
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)  # type: ignore


class ExpensesTable(QtWidgets.QGroupBox):
    """
    Виджет с таблицей расходов
    """
    def __init__(self, exps: list[Expense],  # type: ignore
                 exp_deleter: Callable[[], None],
                 exp_modifier: Callable[[], None],
                 catpk_to_name: Callable[[int], str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Последние расходы</b>")
        self.vbox.addWidget(self.label)
        self.table = ExpensesTableWidget(h_header_str="Дата Сумма Категория Комментарий",
                                         row_count=30)

        self.col_to_attr = {0: "expense_date", 1: "amount", 2: "category", 3: "comment"}

        self.set_expenses(exps)
        self.vbox.addWidget(self.table)

        self.exp_deleter = exp_deleter
        self.exp_modifier = exp_modifier
        self.catpk_to_name = catpk_to_name
        self.exp_del_button = QtWidgets.QPushButton('Удалить')
        self.exp_del_button.clicked.connect(self.delete_exp)  # type: ignore
        self.vbox.addWidget(self.exp_del_button)

        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked)  # type: ignore
        self.table.cellDoubleClicked.connect(self.double_click)  # type: ignore

        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(False)
        self.vbox.addWidget(scroll)
        self.setLayout(self.vbox)

    def set_data(self, data: list[list[str]]) -> None:
        """
        Занос данных в таблицу расходов
        """
        self.table.data = data
        for i, row in enumerate(data):
            for j, x in enumerate(row[:-1]):
                self.table.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x)
                )

    def set_expenses(self, exps: list[Expense]) -> None:
        """
        Занос данных в таблицу расходов из репозитория
        """
        self.expenses = exps
        # self.expenses.sort(key=lambda x: x.expense_date, reverse=True)
        data = []
        for exp in exps:
            name = self.catpk_to_name(exp.category)
            data.append([exp.expense_date, str(exp.amount),
                         str(name), str(exp.comment), exp.pk])
        self.table.clearContents()
        self.set_data(data)  # type: ignore

    def double_click(self) -> None:
        """
        Реакция на двойное нажатие
        """
        self.table.cellChanged.connect(self.modify_exp)  # type: ignore

    def modify_exp(self, row: int, column: int) -> None:
        """
        Изменение при двойном нажатии на ячейку таблицы
        """
        self.table.cellChanged.disconnect(self.modify_exp)  # type: ignore
        pk = self.table.data[row][-1]
        new_val = self.table.item(row, column).text()
        attr = self.col_to_attr[column]
        self.exp_modifier(pk, attr, new_val)  # type: ignore

    def delete_exp(self) -> None:
        """
        Удалить расход
        """
        pks_to_del = []
        chosen_ranges = self.table.selectedRanges()
        for ch_range in chosen_ranges:
            start = ch_range.topRow()
            end = min(ch_range.bottomRow(), len(self.table.data))
            pks_to_del += [i[-1] for i in self.table.data[start:end+1]]
        self.exp_deleter(pks_to_del)  # type: ignore


class BudgetTableWidget(QtWidgets.QTableWidget):
    """
    Таблица бюджета
    """
    data: List[List[Any]] = []

    def __init__(self, *args, row_count: int = 3,  # type: ignore
                 h_header_str: str = "", v_header_str: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(3)
        self.setRowCount(row_count)
        self.row_to_period = {0: "day", 1: "week", 2: "month"}
        hheaders = h_header_str.split()
        self.setHorizontalHeaderLabels(hheaders)
        vheaders = v_header_str.split()
        self.setVerticalHeaderLabels(vheaders)
        for h in [self.horizontalHeader(), self.verticalHeader(),]:
            h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # type: ignore


class BudgetTable(QtWidgets.QGroupBox):
    """
    Виджет с таблицей бюджета
    """
    def __init__(self, budget: list[Budget],    # type: ignore
                 bdg_modifier: Callable[[], None],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bdg_modifier = bdg_modifier
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Бюджет</b>")
        self.vbox.addWidget(self.label)
        self.budget = budget
        self.table = BudgetTableWidget(h_header_str="Бюджет Потрачено Остаток",
                                       v_header_str="День Неделя Месяц",
                                       row_count=3)
        self.row_to_period = {0: "day", 1: "week", 2: "month"}

        self.table.setEditTriggers(
                    QtWidgets.QAbstractItemView.DoubleClicked)  # type: ignore # noqa
        self.table.cellDoubleClicked.connect(self.double_click)  # type: ignore

        self.vbox.addWidget(self.table)
        self.setLayout(self.vbox)

    def set_budget(self, budget: list[Budget]) -> None:
        """
        Установление бюджета из репозитория
        """
        self.budget = budget
        data = []
        for period in ["day", "week", "month"]:
            bdg = [b for b in budget if b.period == period]
            if len(bdg) == 0:
                data.append(["Не установлен", "", "", None])
            else:
                b = bdg[0]
                data.append([str(b.limitation), str(b.spent),
                            str(int(b.limitation) - int(b.spent)), b.pk])  # type: ignore
        self.table.clearContents()
        self.set_data(data)  # type: ignore

    def set_data(self, data: list[list[str]]) -> None:
        """
        Установление бюджета в таблицу
        """
        self.table.data = data
        for i, row in enumerate(data):
            for j, x in enumerate(row[:-1]):
                self.table.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x.capitalize())
                )
                self.table.item(i, j).setTextAlignment(Qt.AlignCenter)  # type: ignore
                if j == 0:
                    self.table.item(i, j).setFlags(Qt.ItemIsEditable  # type: ignore
                                                   | Qt.ItemIsEnabled  # type: ignore
                                                   | Qt.ItemIsSelectable)  # type: ignore
                else:
                    self.table.item(i, j).setFlags(Qt.ItemIsEnabled)  # type: ignore

    def modify_bdg(self, row: int, column: int) -> None:
        """
        Изменение бюджета по двойному нажатию
        """
        self.table.cellChanged.disconnect(self.modify_bdg)  # type: ignore
        pk = self.table.data[row][-1]
        new_limit = self.table.item(row, column).text()
        self.bdg_modifier(pk, new_limit, self.row_to_period[row])  # type: ignore

    def double_click(self) -> None:
        """
        Реакция на двойное нажатие
        """
        self.table.cellChanged.connect(self.modify_bdg)  # type: ignore
