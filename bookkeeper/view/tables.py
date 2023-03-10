from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import *
from bookkeeper.view.labels import GroupLabelCenter
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget

class AnyTableWidget(QtWidgets.QTableWidget):
    def __init__(self, h_header_str:str="", v_header_str:str="", row_count:int=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if h_header_str != "":
            hheaders = h_header_str.split()
            self.setColumnCount(len(hheaders))
            self.setRowCount(row_count)
            self.setHorizontalHeaderLabels(hheaders)
        if v_header_str != "":
            vheaders = v_header_str.split()
            self.setVerticalHeaderLabels(vheaders)
        if h_header_str != "" and v_header_str != "":
            for h in [self.horizontalHeader(), self.verticalHeader(),]:
                h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        else:
            header = self.horizontalHeader()
            print(row_count, hheaders)
            for i in range(len(hheaders)):
                if i == len(hheaders)-1:
                    header.setSectionResizeMode(
                    i, QtWidgets.QHeaderView.Stretch)
                else: 
                    header.setSectionResizeMode(
                    i, QtWidgets.QHeaderView.ResizeToContents)    
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked)
        self.cellDoubleClicked.connect(self.double_click)

        self.verticalHeader().hide()

    def double_click(self, row, columns):
        pass

    def set_data(self, data: list[list[str]]):
        self.data = data
        for i, row in enumerate(data):
            for j, x in enumerate(row[:-1]):
                self.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x)
                )

class ExpensesTable(QtWidgets.QGroupBox):

    def __init__(self, exps:list[Expense], exp_deleter, exp_modifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Последние расходы</b>")
        self.vbox.addWidget(self.label)
        self.table = AnyTableWidget(h_header_str="Дата Сумма Категория Комментарий",\
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

    def set_expenses(self, exps: list[Expense]):
        self.expenses = exps
        self.expenses.sort(key=lambda x: x.expense_date, reverse=True)
        data = []
        for exp in exps:
            data.append([exp.expense_date, str(exp.amount),\
                          str(exp.category), str(exp.comment), exp.pk
                        ])
        self.table.clearContents()
        self.table.set_data(data)

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
        print(pks_to_del)
        self.exp_deleter(pks_to_del)

class BudgetTable(QtWidgets.QGroupBox):
    data = [['День','1000', '999', '1'],
            ['Месяц','7000', '6999', '1'],
            ['Неделя','30000', '29999', '1'],]
    
    def __init__(self, budget:list[Budget], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Бюджет</b>")
        self.vbox.addWidget(self.label)
        self.budget=budget
        self.table = AnyTableWidget(h_header_str="Период Бюджет Потрачено Остаток",\
                                    v_header_str="День Неделя Месяц",\
                                    row_count=3)
        self.table.set_data(self.data)
        self.vbox.addWidget(self.table)
        self.setLayout(self.vbox)

    def set_budget(self, budget: list[Budget]):
        self.budget = budget


        