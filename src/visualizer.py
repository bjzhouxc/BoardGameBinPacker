# src/visualizer.py
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from decimal import Decimal
from typing import List, Dict, Tuple, Optional

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class BinVisualizer:
    """三维装箱结果可视化器"""

    def __init__(self, bin_size: Tuple[float, float, float]):
        self.bin_size = bin_size
        self.fig = None
        self.ax = None

    def _to_float(self, value) -> float:
        if isinstance(value, Decimal):
            return float(value)
        return float(value)

    def _plot_cuboid(self, ax, position, size, color='blue', alpha=0.6,
                     edge_color='black', label=None):
        """绘制单个长方体"""
        x, y, z = [self._to_float(v) for v in position]
        dx, dy, dz = [self._to_float(v) for v in size]

        vertices = np.array([
            [x,    y,    z   ],
            [x+dx, y,    z   ],
            [x+dx, y+dy, z   ],
            [x,    y+dy, z   ],
            [x,    y,    z+dz],
            [x+dx, y,    z+dz],
            [x+dx, y+dy, z+dz],
            [x,    y+dy, z+dz],
        ])

        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]],
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
        ]

        collection = Poly3DCollection(
            faces,
            facecolors=color,
            linewidths=0.8,
            edgecolors=edge_color,
            alpha=alpha,
            label=label
        )
        ax.add_collection3d(collection)

    def _plot_bin_wireframe(self, ax, color='red', linewidth=1.5):
        """绘制箱子线框"""
        A, B, C = self.bin_size

        edges = [
            [(0, 0, 0), (A, 0, 0)],
            [(A, 0, 0), (A, B, 0)],
            [(A, B, 0), (0, B, 0)],
            [(0, B, 0), (0, 0, 0)],
            [(0, 0, C), (A, 0, C)],
            [(A, 0, C), (A, B, C)],
            [(A, B, C), (0, B, C)],
            [(0, B, C), (0, 0, C)],
            [(0, 0, 0), (0, 0, C)],
            [(A, 0, 0), (A, 0, C)],
            [(A, B, 0), (A, B, C)],
            [(0, B, 0), (0, B, C)],
        ]

        for edge in edges:
            xs = [p[0] for p in edge]
            ys = [p[1] for p in edge]
            zs = [p[2] for p in edge]
            ax.plot(xs, ys, zs, color=color, linewidth=linewidth, linestyle='--')

    def visualize(self, items: List[Dict], bin_size: Optional[Tuple] = None,
                  title: str = '3D 装箱结果', show_legend: bool = True,
                  elev: int = 25, azim: int = -60, save_path: Optional[str] = None):
        """可视化单个箱子的装箱结果"""
        if bin_size is None:
            bin_size = self.bin_size

        self.fig = plt.figure(figsize=(12, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')

        self._plot_bin_wireframe(self.ax)

        num_items = len(items)
        if num_items == 0:
            print("⚠️ 该箱子没有物品")
            plt.close()
            return

        colors = plt.cm.tab20(np.linspace(0, 1, max(num_items, 1)))

        for idx, item in enumerate(items):
            name = item.get('name', f'物品{idx+1}')
            position = item.get('position', (0, 0, 0))
            dimensions = item.get('dimensions', (0, 0, 0))

            self._plot_cuboid(
                self.ax,
                position=position,
                size=dimensions,
                color=colors[idx % len(colors)],
                alpha=0.7,
                label=f"{name} ({dimensions[0]:.1f}×{dimensions[1]:.1f}×{dimensions[2]:.1f})"
            )

        A, B, C = bin_size
        self.ax.set_xlim([0, A])
        self.ax.set_ylim([0, B])
        self.ax.set_zlim([0, C])

        self.ax.set_xlabel('X (长)', fontsize=11)
        self.ax.set_ylabel('Y (宽)', fontsize=11)
        self.ax.set_zlabel('Z (高)', fontsize=11)

        self.ax.view_init(elev=elev, azim=azim)

        self.ax.set_title(
            f'{title}\n箱子尺寸: {A}×{B}×{C} | 物品数: {len(items)}',
            fontsize=13, pad=20
        )

        if show_legend and num_items > 0:
            self.ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
                           fontsize=9, framealpha=0.9)

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ 图片已保存到: {save_path}")

        plt.show()

    def visualize_all_bins(self, bins_data: List[List[Dict]],
                           bin_sizes: List[Tuple],
                           title_prefix: str = '箱子',
                           save_dir: Optional[str] = None):
        """可视化所有箱子（每个箱子一张图）"""
        for idx, (items, bin_size) in enumerate(zip(bins_data, bin_sizes)):
            self.bin_size = bin_size

            save_path = None
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f'bin_{idx+1}.png')

            self.visualize(
                items=items,
                bin_size=bin_size,
                title=f'{title_prefix} {idx+1}',
                save_path=save_path
            )