import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtGui import QScreen
from PySide6 import QtWidgets
from bookkeeper.view.tables import ExpensesTable, BudgetTable
from bookkeeper.view.edits import NewExpense


class MainWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vbox = QtWidgets.QVBoxLayout()

        self.budget_table = BudgetTable()
        self.vbox.addWidget(self.budget_table, stretch=6)
        self.new_expense = NewExpense()
        self.vbox.addWidget(self.new_expense, stretch=1)
        self.expenses_table = ExpensesTable()
        self.vbox.addWidget(self.expenses_table, stretch=6)
        self.setLayout(self.vbox)

class MainWindow(QMainWindow):
    def __init__(self, *arg):
        super().__init__()
        self.setWindowTitle("The Bookkeeper App")
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

    # def closeEvent(self, event):
    #     reply = QtWidgets.QMessageBox.question(self, 'Закрыть приложение',
    #     "Вы уверены?\nВсе несохраненные данные будут потеряны.")
    #     if reply == QtWidgets.QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.resize(800, 800)
    window.show()
    sys.exit(app.exec())