# src/gui/widgets.py
from PySide6.QtWidgets import (
    QListWidget, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal


class ItemListWidget(QListWidget):
    """展示桌游/抽屉的列表控件（双击编辑，右键删除）"""

    edit_requested = Signal(int)     # 行号
    delete_requested = Signal(int)   # 行号

    def __init__(self, item_type: str = "item", parent=None):
        super().__init__(parent)
        self.item_type = item_type
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        self.itemDoubleClicked.connect(self._on_double_click)

    def _show_menu(self, pos):
        item = self.itemAt(pos)
        if item is None:
            return
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == edit_action:
            self.edit_requested.emit(self.row(item))
        elif action == delete_action:
            self._delete_item(item)

    def _on_double_click(self, item):
        self.edit_requested.emit(self.row(item))

    def _delete_item(self, item):
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除「{item.text()}」吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            row = self.row(item)
            self.takeItem(row)
            self.delete_requested.emit(row)