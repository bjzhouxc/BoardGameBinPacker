# src/gui/main_window.py
import os
import json

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QGroupBox, QMessageBox, QFileDialog, QSplitter,
    QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from src.gui.dialogs import ItemDialog, DrawerDialog
from src.gui.widgets import ItemListWidget
from src.packer import ThreeDBoxPacker
from src.visualizer import BinFigureBuilder


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("桌游收纳整理器")
        self.resize(1400, 800)

        self.drawers = []
        self.items = []

        # ✅ 新增：保存装箱结果
        self.current_results = None
        self.current_bin_dims = None

        self._init_ui()

    # ==================== UI 初始化 ====================

    def _init_ui(self):
        # 主分栏
        splitter = QSplitter(Qt.Horizontal)

        # 左栏
        left_panel = self._build_left_panel()
        splitter.addWidget(left_panel)

        # 右栏
        right_panel = self._build_right_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([400, 1000])

        self.setCentralWidget(splitter)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ---- 抽屉区域 ----
        drawer_group = QGroupBox("📦 抽屉列表")
        drawer_layout = QVBoxLayout(drawer_group)

        self.drawer_list = ItemListWidget("drawer")
        self.drawer_list.setMinimumHeight(150)
        self.drawer_list.edit_requested.connect(self._edit_drawer)
        self.drawer_list.delete_requested.connect(self._delete_drawer)
        drawer_layout.addWidget(self.drawer_list)

        btn_add_drawer = QPushButton("➕ 新增抽屉信息")
        btn_add_drawer.clicked.connect(self._add_drawer)
        drawer_layout.addWidget(btn_add_drawer)

        layout.addWidget(drawer_group)

        # ---- 桌游区域 ----
        item_group = QGroupBox("🎲 桌游列表")
        item_layout = QVBoxLayout(item_group)

        self.item_list = ItemListWidget("item")
        self.item_list.setMinimumHeight(250)
        self.item_list.edit_requested.connect(self._edit_item)
        self.item_list.delete_requested.connect(self._delete_item)
        item_layout.addWidget(self.item_list)

        btn_add_item = QPushButton("➕ 新增桌游信息")
        btn_add_item.clicked.connect(self._add_item)
        item_layout.addWidget(btn_add_item)

        layout.addWidget(item_group)

        # ---- 文件操作 ----
        io_group = QGroupBox("💾 文件操作")
        io_layout = QVBoxLayout(io_group)

        btn_save = QPushButton("保存为 JSON")
        btn_save.clicked.connect(self._save_json)
        io_layout.addWidget(btn_save)

        btn_load = QPushButton("读取 JSON")
        btn_load.clicked.connect(self._load_json)
        io_layout.addWidget(btn_load)

        layout.addWidget(io_group)

        # ---- 开始整理 ----
        self.btn_pack = QPushButton("🚀 开始整理")
        self.btn_pack.setMinimumHeight(45)
        self.btn_pack.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        self.btn_pack.clicked.connect(self._start_packing)
        layout.addWidget(self.btn_pack)

        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 顶部工具条：选择显示哪个箱子
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("显示箱子:"))
        self.bin_selector = QComboBox()
        self.bin_selector.currentIndexChanged.connect(self._on_bin_changed)
        self.bin_selector.setMinimumWidth(200)
        top_bar.addWidget(self.bin_selector)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Matplotlib 画布
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # 结果摘要
        self.summary_label = QLabel("请点击「开始整理」以查看结果")
        self.summary_label.setAlignment(Qt.AlignLeft)
        self.summary_label.setStyleSheet("color: #555; padding: 4px;")
        layout.addWidget(self.summary_label)

        return panel

    # ==================== 抽屉相关操作 ====================

    def _add_drawer(self):
        dlg = DrawerDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            self.drawers.append(data)
            self._refresh_drawer_list()

    def _edit_drawer(self, row: int):
        if row < 0 or row >= len(self.drawers):
            return
        dlg = DrawerDialog(self, drawer=self.drawers[row])
        if dlg.exec():
            self.drawers[row] = dlg.get_data()
            self._refresh_drawer_list()

    def _delete_drawer(self, row: int):
        if 0 <= row < len(self.drawers):
            self.drawers.pop(row)

    def _refresh_drawer_list(self):
        self.drawer_list.clear()
        for d in self.drawers:
            text = f"{d['name']}  ({d['w']:.1f}×{d['h']:.1f}×{d['d']:.1f})"
            self.drawer_list.addItem(text)

    # ==================== 桌游相关操作 ====================

    def _add_item(self):
        dlg = ItemDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            self.items.append(data)
            self._refresh_item_list()

    def _edit_item(self, row: int):
        if row < 0 or row >= len(self.items):
            return
        dlg = ItemDialog(self, item=self.items[row])
        if dlg.exec():
            self.items[row] = dlg.get_data()
            self._refresh_item_list()

    def _delete_item(self, row: int):
        if 0 <= row < len(self.items):
            self.items.pop(row)

    def _refresh_item_list(self):
        self.item_list.clear()
        for it in self.items:
            text = f"{it['name']}  ({it['w']:.1f}×{it['h']:.1f}×{it['d']:.1f})"
            self.item_list.addItem(text)

    # ==================== 文件操作 ====================

    def _save_json(self):
        if not self.drawers and not self.items:
            QMessageBox.information(self, "提示", "当前没有数据可保存")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "保存数据", "data/packing_data.json", "JSON Files (*.json)"
        )
        if not filepath:
            return

        try:
            data = {
                "config": {
                    "bigger_first": True,
                    "max_weight": 1000,
                },
                "bins": [
                    {"id": d['name'], "width": d['w'],
                     "height": d['h'], "depth": d['d']}
                    for d in self.drawers
                ],
                "items": [
                    {"name": it['name'], "width": it['w'],
                     "height": it['h'], "depth": it['d'],
                     "weight": it.get('weight', 1)}
                    for it in self.items
                ],
            }
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", f"已保存到:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def _load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "读取数据", "data", "JSON Files (*.json)"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 读取抽屉
            self.drawers = []
            for b in data.get('bins', []):
                self.drawers.append({
                    'name': b.get('id') or b.get('name', '未命名'),
                    'w': float(b.get('width', 0)),
                    'h': float(b.get('height', 0)),
                    'd': float(b.get('depth', 0)),
                })

            # 读取桌游
            self.items = []
            for it in data.get('items', []):
                self.items.append({
                    'name': it.get('name', '未命名'),
                    'w': float(it.get('width', 0)),
                    'h': float(it.get('height', 0)),
                    'd': float(it.get('depth', 0)),
                    'weight': float(it.get('weight', 1)),
                })

            self._refresh_drawer_list()
            self._refresh_item_list()
            QMessageBox.information(
                self, "成功",
                f"已加载:\n抽屉 {len(self.drawers)} 个\n桌游 {len(self.items)} 个"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取失败:\n{e}")

    # ==================== 执行装箱 ====================

    def _start_packing(self):
        if not self.drawers:
            QMessageBox.warning(self, "提示", "请先新增至少一个抽屉")
            return
        if not self.items:
            QMessageBox.warning(self, "提示", "请先新增至少一个桌游")
            return

        try:
            bin_dims = [(d['w'], d['h'], d['d']) for d in self.drawers]
            items_data = [
                {
                    'name': it['name'],
                    'w': it['w'],
                    'h': it['h'],
                    'd': it['d'],
                    'weight': it.get('weight', 1),
                }
                for it in self.items
            ]

            packer = ThreeDBoxPacker(bin_dims)
            results = packer.pack_items(items_data, bigger_first=True)

            # ✅ 保存结果到 self.current_results
            self.current_results = results
            self.current_bin_dims = bin_dims

            # 更新下拉选择框
            self.bin_selector.blockSignals(True)
            self.bin_selector.clear()
            for i, bin_result in enumerate(results['bins']):
                self.bin_selector.addItem(
                    f"抽屉 {i + 1}: {self.drawers[i]['name']} "
                    f"({bin_result['item_count']} 个)"
                )
            self.bin_selector.blockSignals(False)

            # 显示第一个箱子
            if results['bins']:
                self._render_figure(0)

            summary = (
                f"总物品数: {results['total_items']}  |  "
                f"✅ 放入: {results['placed_count']}  |  "
                f"❌ 未放入: {results['unplaced_count']}"
            )
            self.summary_label.setText(summary)

            if results['unplaced_count'] > 0:
                unplaced = [it['name'] for it in results['unplaced_items']]
                QMessageBox.warning(
                    self, "提示",
                    f"有 {results['unplaced_count']} 个物品无法放入任何抽屉:\n"
                    + "\n".join(f"  • {n}" for n in unplaced[:20])
                    + ("\n  ..." if len(unplaced) > 20 else "")
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"装箱失败:\n{e}")

    def _on_bin_changed(self, index: int):
        if 0 <= index < len(self.current_results):
            self._render_figure(index)

    def _render_figure(self, index: int):
        """把指定箱子的装箱结果绘制到固定画布上"""
        if self.current_results is None:
            return
        if index < 0 or index >= len(self.current_results['bins']):
            return

        bin_result = self.current_results['bins'][index]
        bin_size = self.current_bin_dims[index]

        builder = BinFigureBuilder(bin_size=bin_size)
        builder.draw_on_figure(
            fig=self.canvas.figure,          # ✅ 使用固定画布
            items=bin_result['items'],
            title=f"抽屉 {index+1}: {self.drawers[index]['name']}",
        )

        # ✅ 同步 Matplotlib 工具栏（让它知道当前 axes 变了）
        self.canvas.draw_idle()