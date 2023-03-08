from PySide6 import QtWidgets
from PySide6.QtCore import Qt

class LabeledLineInput(QtWidgets.QWidget):
    def __init__(self, text, placeholder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)
        self.input = QtWidgets.QLineEdit(self.placeholder)
        self.layout.addWidget(self.input, stretch=5)
        self.setLayout(self.layout)

    def clear(self):
        self.input.setText(self.placeholder)

    def text(self):
        return self.input.text()

class LabeledComboBoxInput(QtWidgets.QWidget):
    def __init__(self, text: str, items: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.combo_box.setMaxVisibleItems(16)
        self.set_items(items)
        self.combo_box.setEditable(False)
        self.layout.addWidget(self.combo_box, stretch=5)

        self.setLayout(self.layout)

    def clear(self):
        self.combo_box.setCurrentText(self.combo_box.placeholderText())

    def text(self):
        return self.combo_box.currentText()
    
    def set_items(self, items: list[str]):
        self.items = items
        self.combo_box.clear()
        self.combo_box.addItems(items)
        if len(items) != 0:
            self.combo_box.setPlaceholderText(items[0])
        else:
            self.combo_box.setPlaceholderText("")
        self.clear()
        
class GroupLabelCenter(QtWidgets.QLabel):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
