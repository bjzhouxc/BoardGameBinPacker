# src/visualizer.py
import os
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.figure import Figure
import numpy as np
from decimal import Decimal
from typing import List, Dict, Tuple, Optional

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class BinFigureBuilder:
    """
    构造 Matplotlib Figure 对象（供 Qt 嵌入使用）
    坐标系说明：
      py3dbp: position=(x, y, z)，x=宽方向, y=高方向, z=深方向
      Matplotlib: X=宽, Y=深, Z=高
      转换规则: (x, y, z) -> (x, z, y)
    """

    def __init__(self, bin_size: Tuple[float, float, float]):
        """
        :param bin_size: 箱子尺寸 (width, height, depth)
        """
        self.bin_size = bin_size

    def _to_float(self, value) -> float:
        if isinstance(value, Decimal):
            return float(value)
        return float(value)

    def _map_coords(self, position, size):
        """py3dbp 的 (x,y,z)+(w,h,d) 映射到 Matplotlib 的 (X,Y,Z)+(dX,dY,dZ)"""
        px, py, pz = [self._to_float(v) for v in position]
        pw, ph, pd = [self._to_float(v) for v in size]
        x, y, z = px, pz, py
        dx, dy, dz = pw, pd, ph
        return (x, y, z), (dx, dy, dz)

    def _plot_cuboid(self, ax, position, size, color='blue', alpha=0.6,
                     edge_color='black', label=None):
        (x, y, z), (dx, dy, dz) = self._map_coords(position, size)
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
            faces, facecolors=color, linewidths=0.8,
            edgecolors=edge_color, alpha=alpha, label=label
        )
        ax.add_collection3d(collection)

    def _plot_bin_wireframe(self, ax, color='red', linewidth=1.5):
        w, h, d = self.bin_size
        X, Y, Z = w, d, h
        edges = [
            [(0, 0, 0), (X, 0, 0)], [(X, 0, 0), (X, Y, 0)],
            [(X, Y, 0), (0, Y, 0)], [(0, Y, 0), (0, 0, 0)],
            [(0, 0, Z), (X, 0, Z)], [(X, 0, Z), (X, Y, Z)],
            [(X, Y, Z), (0, Y, Z)], [(0, Y, Z), (0, 0, Z)],
            [(0, 0, 0), (0, 0, Z)], [(X, 0, 0), (X, 0, Z)],
            [(X, Y, 0), (X, Y, Z)], [(0, Y, 0), (0, Y, Z)],
        ]
        for edge in edges:
            xs = [p[0] for p in edge]
            ys = [p[1] for p in edge]
            zs = [p[2] for p in edge]
            ax.plot(xs, ys, zs, color=color, linewidth=linewidth, linestyle='--')

    def draw_on_figure(self, fig: Figure, items: List[Dict],
                       title: str = '3D 装箱结果',
                       show_legend: bool = True,
                       elev: int = 25, azim: int = -60):
        """
        在给定的 Figure 对象上绘制装箱结果（清空后重绘）
        """
        fig.clear()
        ax = fig.add_subplot(111, projection='3d')

        self._plot_bin_wireframe(ax)

        num_items = len(items)
        if num_items > 0:
            colors = plt.cm.tab20(np.linspace(0, 1, max(num_items, 1)))
            for idx, item in enumerate(items):
                name = item.get('name', f'物品{idx+1}')
                position = item.get('position', (0, 0, 0))
                dimensions = item.get('dimensions', (0, 0, 0))
                self._plot_cuboid(
                    ax,
                    position=position,
                    size=dimensions,
                    color=colors[idx % len(colors)],
                    alpha=0.7,
                    label=f"{name} ({dimensions[0]:.1f}×{dimensions[1]:.1f}×{dimensions[2]:.1f})"
                )

        w, h, d = self.bin_size
        ax.set_xlim([0, w])
        ax.set_ylim([0, d])
        ax.set_zlim([0, h])
        ax.set_xlabel('X (宽 width)', fontsize=9)
        ax.set_ylabel('Y (深 depth)', fontsize=9)
        ax.set_zlabel('Z (高 height)', fontsize=9)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f'{title}\n箱子尺寸: {w}×{h}×{d} | 物品数: {num_items}',
                     fontsize=11, pad=15)

        try:
            ax.set_box_aspect([w, d, h])
        except Exception:
            pass

        if show_legend and num_items > 0:
            ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
                      fontsize=7, framealpha=0.9)

        fig.tight_layout()
        return ax