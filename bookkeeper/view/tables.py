from PySide6 import QtWidgets
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
        #TODO triggers
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()

    def set_data(self, data: list[list[str]]):
        for i, row in enumerate(data):
            for j, x in enumerate(row):
                self.setItem(
                    i, j,
                    QtWidgets.QTableWidgetItem(x.capitalize())
                )

class ExpensesTable(QtWidgets.QGroupBox):
    data = [["2023-02-03 15:30:00", str(100), "ме", ""],
            ["2023-02-03 15:00:00", str(500), "одежда", ""],
            ["2023-02-03 15:30:00", str(500), "мясо", ""],
            ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Последние расходы</b>")
        self.vbox.addWidget(self.label)
        self.table = AnyTableWidget(h_header_str="Дата Сумма Категория Комментарий",\
                                     row_count=15)
        self.table.set_data(self.data)
        self.vbox.addWidget(self.table)
        scroll = QtWidgets.QScrollArea(self)
        self.vbox.addWidget(scroll)
        scroll.setWidgetResizable(True)
        self.setLayout(self.vbox)
    def set_expenses(self, exps: list[Expense]):
        self.expenses = exps

class BudgetTable(QtWidgets.QGroupBox):
    data = [['День','1000', '999', '1'],
            ['Месяц','7000', '6999', '1'],
            ['Неделя','30000', '29999', '1'],]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()
        self.label = GroupLabelCenter("<b>Бюджет</b>")
        self.vbox.addWidget(self.label)
        self.table = AnyTableWidget(h_header_str="Период Бюджет Потрачено Остаток",\
                                    v_header_str="День Неделя Месяц",\
                                    row_count=3)
        self.table.set_data(self.data)
        self.vbox.addWidget(self.table)
        scroll = QtWidgets.QScrollArea(self)
        self.vbox.addWidget(scroll)
        scroll.setWidgetResizable(True)
        self.setLayout(self.vbox)
    def set_budget(self, budget: list[Budget]):
        self.budget = budget


        