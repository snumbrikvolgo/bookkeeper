"""
Тесты GUI для окна с редактированием списка категорий
"""
from pytestqt.qt_compat import qt_api
from bookkeeper.view.edits import CategoryEditWindow
from bookkeeper.models.category import Category

cat_adder = lambda name, parent: None 
cat_deleter = lambda cat_name: None
cat_checker = lambda parent_name: None
cat_modifier = lambda parent_name: None
def test_create_window(qtbot):
    widget = CategoryEditWindow([], cat_adder, cat_deleter, cat_modifier)
    qtbot.addWidget(widget)
    assert widget.cat_adder == cat_adder
    assert widget.cat_deleter == cat_deleter

def test_set_categories(qtbot):
    widget = CategoryEditWindow([], cat_adder, cat_deleter, cat_modifier)
    qtbot.addWidget(widget)
    cats = [Category("cat1", pk=1), 
            Category("cat2", pk=2),
            Category("cat11", pk=11, parent=1), 
            Category("cat12", pk=12, parent=1),
            Category("cat121", pk=121, parent=12)]
    widget.set_categories(cats)
    assert widget.categories == cats
    assert widget.cat_names == [c.name for c in cats]
    assert widget.cats_tree.topLevelItem(0).text(0) == "cat1"
    assert widget.cats_tree.topLevelItem(1).text(0) == "cat2"
    assert widget.cats_tree.topLevelItem(0).child(0).text(0) == "cat11"
    assert widget.cats_tree.topLevelItem(0).child(1).text(0) == "cat12"
    assert widget.cats_tree.topLevelItem(0).child(1).child(0).text(0) == "cat121"

def test_once_clicked(qtbot):
    widget = CategoryEditWindow([Category("cat1", pk=1)], 
                                  cat_adder, cat_deleter, cat_modifier)
    qtbot.addWidget(widget)
    item = widget.cats_tree.topLevelItem(0)
    widget.cats_tree.itemClicked.emit(item, 0)
    clicked_cat_name = item.text(0)
    assert widget.cat_del.text() == clicked_cat_name
    assert widget.cat_add_parent.text() == clicked_cat_name

def test_delete_category(qtbot):
    def cat_deleter(cat_name):
        cat_deleter.was_called = True
        assert cat_name == "cat1"
    cat_deleter.was_called = False
    widget = CategoryEditWindow([Category("cat1", pk=1)], 
                                   cat_adder, cat_deleter, cat_modifier)
    qtbot.addWidget(widget)
    widget.cat_del.set_text("cat1")
    qtbot.mouseClick(
                widget.cat_del_button,
                qt_api.QtCore.Qt.MouseButton.LeftButton
            )
    assert cat_deleter.was_called == True
    
def test_add_category(qtbot):
    def cat_adder(name, parent):
        cat_adder.was_called = True
        assert name == "cat12"
        assert parent == "cat1"
    cat_adder.was_called = False
    widget = CategoryEditWindow([Category("cat1", pk=1)], 
                                   cat_adder, cat_deleter, cat_modifier)
    qtbot.addWidget(widget)
    widget.cat_add_name.set_text("cat12")
    widget.cat_add_parent.set_text("cat1")
    qtbot.mouseClick(
                widget.cat_add_button,
                qt_api.QtCore.Qt.MouseButton.LeftButton
            )
    assert cat_adder.was_called == True

def test_add_category_no_parent(qtbot):
    def cat_adder(name, parent):
        cat_adder.was_called = True
        assert name == "cat1"
        assert parent == None
    cat_adder.was_called = False
    widget = CategoryEditWindow([], cat_adder, cat_deleter, cat_modifier)
    qtbot.addWidget(widget)
    widget.cat_add_name.set_text("cat1")
    widget.cat_add_parent.set_text("- Без родительской категории -")
    qtbot.mouseClick(
                widget.cat_add_button,
                qt_api.QtCore.Qt.MouseButton.LeftButton
            )
    add_name_text = widget.cat_add_name.text()
    widget.cat_add_name.clear()
    assert add_name_text == widget.cat_add_name.text()
    add_parent_text = widget.cat_add_parent.text()
    widget.cat_add_parent.clear()
    assert add_parent_text == widget.cat_add_parent.text()
    assert cat_adder.was_called == True