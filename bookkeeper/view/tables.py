from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import *
from bookkeeper.view.labels import GroupLabelCenter
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget

class ExpensesTableWidget(QtWidgets.QTableWidget):
    def __init__(self, h_header_str:str="", row_count:int=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(4)
        self.setRowCount(row_count)
        self.headers = h_header_str.split()
        self.col_to_attr = {0:"expense_date", 1:"amount", 2:"category", 3:"comment"}
        self.setHorizontalHeaderLabels(self.headers)
        header = self.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

class ExpensesTable(QtWidgets.QGroupBox):

    def __init__(self, exps:list[Expense], exp_deleter, exp_modifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Последние расходы</b>")
        self.vbox.addWidget(self.label)
        self.table = ExpensesTableWidget(h_header_str="Дата Сумма Категория Комментарий",\
                                     row_count=30)
        
        self.col_to_attr = {0:"expense_date", 1:"amount", 2:"category", 3:"comment"}

        self.set_expenses(exps)
        self.vbox.addWidget(self.table)
        
        self.exp_deleter = exp_deleter
        self.exp_modifier = exp_modifier

        self.exp_del_button = QtWidgets.QPushButton('Удалить')
        self.exp_del_button.clicked.connect(self.delete_exp)
        self.vbox.addWidget(self.exp_del_button)

        self.exp_mod_button = QtWidgets.QPushButton('Изменить')
        self.exp_mod_button.clicked.connect(self.modify_button)
        self.vbox.addWidget(self.exp_mod_button)

        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked)
        self.table.cellDoubleClicked.connect(self.double_click)

        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(False)
        self.vbox.addWidget(scroll)
        self.setLayout(self.vbox)

    def set_data(self, data: list[list[str]]):
        self.table.data = data
        for i, row in enumerate(data):
            for j, x in enumerate(row[:-1]):
                self.table.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x)
                )

    def set_expenses(self, exps: list[Expense]):
        self.expenses = exps
        self.expenses.sort(key=lambda x: x.expense_date, reverse=True)
        data = []
        for exp in exps:
            data.append([exp.expense_date, str(exp.amount),\
                          str(exp.category), str(exp.comment), exp.pk
                        ])
        self.table.clearContents()
        self.set_data(data)

    def double_click(self, row, columns):
        self.table.cellChanged.connect(self.modify_exp)

    def modify_button(self):
        self.table.cellClicked.connect(self.modify_exp_button)

    def modify_exp_button(self, row, column):
        old_val = self.table.item(row, column).text()
        self.table.cellClicked.disconnect(self.modify_exp_button)
        pk = self.table.data[row][-1]
        new_val = self.table.item(row, column).text()
        attr = self.col_to_attr[column]
        self.exp_modifier(pk, attr, new_val, old_val)

    def modify_exp(self, row, column):
        old_val = self.table.item(row, column).text()
        self.table.cellChanged.disconnect(self.modify_exp)
        pk = self.table.data[row][-1]
        new_val = self.table.item(row, column).text()
        attr = self.col_to_attr[column]
        self.exp_modifier(pk, attr, new_val, old_val)

    def delete_exp(self):
        pks_to_del = []
        chosen_ranges = self.table.selectedRanges()
        for ch_range in chosen_ranges:
            start = ch_range.topRow()
            end = min(ch_range.bottomRow(), len(self.table.data))
            pks_to_del += [i[-1] for i in self.table.data[start:end+1]]
        self.exp_deleter(pks_to_del)

class BudgetTableWidget(QtWidgets.QTableWidget):
    def __init__(self, h_header_str:str="", v_header_str:str="", row_count:int=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(3)
        self.setRowCount(row_count)
        self.row_to_period = {0:"day", 1:"week", 2:"month"}
        hheaders = h_header_str.split()
        self.setHorizontalHeaderLabels(hheaders)
        vheaders = v_header_str.split()
        self.setVerticalHeaderLabels(vheaders)
        for h in [self.horizontalHeader(), self.verticalHeader(),]:
            h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)   

class BudgetTable(QtWidgets.QGroupBox):
    def __init__(self, budget:list[Budget], bdg_modifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bdg_modifier = bdg_modifier
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Бюджет</b>")
        self.vbox.addWidget(self.label)
        self.budget=budget
        self.table = BudgetTableWidget(h_header_str="Бюджет Потрачено Остаток",\
                                    v_header_str="День Неделя Месяц",\
                                    row_count=3)
        self.row_to_period = {0:"day", 1:"week", 2:"month"}

        self.table.setEditTriggers(
        QtWidgets.QAbstractItemView.DoubleClicked)
        self.table.cellDoubleClicked.connect(self.double_click)

        self.vbox.addWidget(self.table)
        self.setLayout(self.vbox)

    def set_budget(self, budget: list[Budget]):
        self.budget = budget
        data = []
        for period in ["day", "week", "month"]:
            bdg = [b for b in budget if b.period == period]
            if len(bdg) == 0:
                data.append(["Не установлен", "", "", None])
            else:
                b = bdg[0]
                data.append([str(b.limitation), str(b.spent),
                            str(int(b.limitation) - int(b.spent)), b.pk])
        self.table.clearContents()
        self.set_data(data)

    def set_data(self, data: list[list[str]]):
        self.table.data = data
        for i, row in enumerate(data):
            for j, x in enumerate(row[:-1]):
                self.table.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x.capitalize())
                )
                self.table.item(i, j).setTextAlignment(Qt.AlignCenter)
                if j == 0:
                    self.table.item(i, j).setFlags(Qt.ItemIsEditable 
                                             | Qt.ItemIsEnabled 
                                             | Qt.ItemIsSelectable)
                else: 
                    self.table.item(i, j).setFlags(Qt.ItemIsEnabled)

    def modify_bdg(self, row, column):
        self.table.cellChanged.disconnect(self.modify_bdg)
        pk = self.table.data[row][-1]
        new_limit = self.table.item(row, column).text()
        self.bdg_modifier(pk, new_limit, self.row_to_period[row])

    def double_click(self, row, columns):
        self.table.cellChanged.connect(self.modify_bdg)
