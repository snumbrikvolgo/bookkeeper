"""
Тесты GUI для модуля с добавлением новой траты
"""
from pytestqt.qt_compat import qt_api

from bookkeeper.view.edits import NewExpense
from bookkeeper.models.category import Category

show_category_edit_window = lambda: None
exp_adder = lambda amount, cat_name, comment: None

def test_create_group(qtbot):
    widget = NewExpense([], 
                             show_category_edit_window, 
                             exp_adder,)
    qtbot.addWidget(widget)
    assert widget.show_category_edit_window == show_category_edit_window
    assert widget.exp_adder == exp_adder

def test_set_categories(qtbot):
    widget = NewExpense([], 
                             show_category_edit_window, 
                             exp_adder,)
    qtbot.addWidget(widget)
    cats = [Category("cat1"), Category("cat2"),]
    widget.set_categories(cats)
    assert widget.categories == cats
    assert widget.cat_names == [c.name for c in cats]

def test_add_expense(qtbot):
    def exp_adder(amount, cat_name, comment):
        exp_adder.was_called = True
        assert amount == "100"
        assert cat_name == "cat1"
        assert comment == "test"
    exp_adder.was_called = False
    cats = [Category("cat1"), Category("cat2"),]
    widget = NewExpense(cats, 
                             show_category_edit_window, 
                             exp_adder,)
    qtbot.addWidget(widget)
    widget.amount_input.set_text("100")
    widget.category_input.set_text("cat1")
    widget.comment_input.set_text("test")
    qtbot.mouseClick(
                widget.submit_button,
                qt_api.QtCore.Qt.MouseButton.LeftButton
            )
    assert exp_adder.was_called == True
     