# main.py
import os
import sys

# 保证能 import src
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 提前设置 Matplotlib 缓存路径，避免打包后临时目录问题
os.environ.setdefault(
    'MPLCONFIGDIR',
    os.path.join(PROJECT_ROOT, '.matplotlib_cache')
)

import matplotlib
matplotlib.use('QtAgg')  # 让 Matplotlib 使用 Qt 后端

from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()