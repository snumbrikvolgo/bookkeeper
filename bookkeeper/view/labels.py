"""
Классы текстовых полей
"""
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
# pylint: disable = no-name-in-module
# pylint: disable=c-extension-no-member
# pylint: disable=too-few-public-methods


class LabeledLineInput(QtWidgets.QWidget):
    """
    Поле для линейного ввода
    """
    def __init__(self, text: str, placeholder: str, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.layout = QtWidgets.QHBoxLayout()  # type: ignore
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)  # type: ignore
        self.input = QtWidgets.QLineEdit(self.placeholder)
        self.layout.addWidget(self.input, stretch=5)  # type: ignore
        self.setLayout(self.layout)  # type: ignore

    def clear(self) -> None:
        """
        Очистить
        """
        self.input.setText(self.placeholder)

    def set_text(self, text: str) -> None:
        """
        Установить текст
        """
        self.input.setText(text)

    def text(self) -> str:
        """
        Вернуть текст
        """
        return self.input.text()


class LabeledComboBoxInput(QtWidgets.QWidget):
    """
    Класс выдвигающегося списка
    """
    def __init__(self, text: str, items: list[str], *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()  # type: ignore
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label, stretch=1)  # type: ignore
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # type: ignore # noqa
        self.combo_box.setMaxVisibleItems(16)
        self.set_items(items)
        self.combo_box.setEditable(False)
        self.layout.addWidget(self.combo_box, stretch=5)  # type: ignore

        self.setLayout(self.layout)  # type: ignore

    def clear(self) -> None:
        """
        Очистить
        """
        self.combo_box.setCurrentText(self.combo_box.placeholderText())

    def text(self) -> str:
        """
        Вернуть текст
        """
        return self.combo_box.currentText()

    def set_text(self, text: str) -> None:
        """
        Установить текст
        """
        self.combo_box.setCurrentText(text)

    def set_items(self, items: list[str]) -> None:
        """
        Установить поля в выдвигающемся списке
        """
        self.items = items
        self.combo_box.clear()
        self.combo_box.addItems(items)
        if len(items) != 0:
            self.combo_box.setPlaceholderText(items[0])
        else:
            self.combo_box.setPlaceholderText("")
        self.clear()


class GroupLabelCenter(QtWidgets.QLabel):
    """
    Поставить по центру надпись
    """
    def __init__(self, text: str, *args, **kwargs):  # type: ignore
        super().__init__(text, *args, **kwargs)
        self.setAlignment(Qt.AlignCenter)  # type: ignore
