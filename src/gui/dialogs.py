# src/gui/dialogs.py
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox,
    QVBoxLayout, QMessageBox
)


class ItemDialog(QDialog):
    """新增/编辑桌游物品对话框"""

    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("编辑桌游" if item else "新增桌游")
        self.setMinimumWidth(320)

        self.item = item or {}

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(self.item.get('name', ''))
        self.name_edit.setPlaceholderText("例如：炸弹猫：灾厄菜谱")

        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 9999)
        self.width_spin.setDecimals(2)
        self.width_spin.setValue(float(self.item.get('w', 1.0)))
        self.width_spin.setSuffix(" cm")

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 9999)
        self.height_spin.setDecimals(2)
        self.height_spin.setValue(float(self.item.get('h', 1.0)))
        self.height_spin.setSuffix(" cm")

        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0.1, 9999)
        self.depth_spin.setDecimals(2)
        self.depth_spin.setValue(float(self.item.get('d', 1.0)))
        self.depth_spin.setSuffix(" cm")

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.0, 9999)
        self.weight_spin.setDecimals(2)
        self.weight_spin.setValue(float(self.item.get('weight', 1.0)))
        self.weight_spin.setSuffix(" g")

        form.addRow("名称:", self.name_edit)
        form.addRow("长 (width):", self.width_spin)
        form.addRow("宽 (height):", self.height_spin)
        form.addRow("高 (depth):", self.depth_spin)
        form.addRow("重量:", self.weight_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "提示", "名称不能为空")
            return
        self.accept()

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'w': self.width_spin.value(),
            'h': self.height_spin.value(),
            'd': self.depth_spin.value(),
            'weight': self.weight_spin.value(),
        }


class DrawerDialog(QDialog):
    """新增/编辑抽屉对话框"""

    def __init__(self, parent=None, drawer=None):
        super().__init__(parent)
        self.setWindowTitle("编辑抽屉" if drawer else "新增抽屉")
        self.setMinimumWidth(320)

        self.drawer = drawer or {}

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(self.drawer.get('name', ''))
        self.name_edit.setPlaceholderText("例如：书桌抽屉1")

        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 9999)
        self.width_spin.setDecimals(2)
        self.width_spin.setValue(float(self.drawer.get('w', 50.0)))
        self.width_spin.setSuffix(" cm")

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 9999)
        self.height_spin.setDecimals(2)
        self.height_spin.setValue(float(self.drawer.get('h', 30.0)))
        self.height_spin.setSuffix(" cm")

        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0.1, 9999)
        self.depth_spin.setDecimals(2)
        self.depth_spin.setValue(float(self.drawer.get('d', 40.0)))
        self.depth_spin.setSuffix(" cm")

        form.addRow("名称:", self.name_edit)
        form.addRow("宽 (width):", self.width_spin)
        form.addRow("高 (height):", self.height_spin)
        form.addRow("深 (depth):", self.depth_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "提示", "名称不能为空")
            return
        self.accept()

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'w': self.width_spin.value(),
            'h': self.height_spin.value(),
            'd': self.depth_spin.value(),
        }