# src/packer.py
from py3dbp import Packer, Bin, Item
from typing import List, Dict, Tuple
from decimal import Decimal


class ThreeDBoxPacker:
    def __init__(self, bin_dimensions: List[Tuple[float, float, float]]):
        """
        初始化装箱器
        :param bin_dimensions: 箱子的尺寸列表 [(A1,B1,C1), (A2,B2,C2), ...]
        """
        self.packer = Packer()
        self.bin_dimensions = bin_dimensions
        self._setup_bins()

    def _setup_bins(self):
        """根据箱子尺寸创建Bin对象"""
        for i, (w, h, d) in enumerate(self.bin_dimensions, 1):
            self.packer.add_bin(Bin(f'箱子{i}号', w, h, d, 1000))

    def pack_items(self, items_data: List[Dict], bigger_first: bool = True) -> Dict:
        """
        执行装箱
        :param items_data: 物品列表
        :param bigger_first: 是否优先放大的物品
        :return: 装箱结果统计
        """
        self.packer.items = []

        for item in items_data:
            self.packer.add_item(
                Item(
                    item['name'],
                    item['w'],
                    item['h'],
                    item['d'],
                    item.get('weight', 1)
                )
            )

        self.packer.pack(bigger_first=bigger_first, distribute_items=True)

        return self._parse_results_improved(items_data)

    def _get_actual_dimensions(self, item) -> Tuple[float, float, float]:
        """
        根据 rotation_type 返回物品实际占用空间的尺寸
        py3dbp 的 rotation_type 对照表（6 种旋转）:
            0: (width,  height, depth)
            1: (height, width,  depth)
            2: (height, depth,  width)
            3: (depth,  height, width)
            4: (depth,  width,  height)
            5: (width,  depth,  height)
        :return: (X方向尺寸, Y方向尺寸, Z方向尺寸)
        """
        w = float(getattr(item, 'width', 0))
        h = float(getattr(item, 'height', 0))
        d = float(getattr(item, 'depth', 0))
        rt = getattr(item, 'rotation_type', 0)

        rotation_map = {
            0: (w, h, d),
            1: (h, w, d),
            2: (h, d, w),
            3: (d, h, w),
            4: (d, w, h),
            5: (w, d, h),
        }
        return rotation_map.get(rt, (w, h, d))

    def _parse_results_improved(self, items_data: List[Dict]) -> Dict:
        """改进的结果解析：包含物品位置信息和实际旋转后的尺寸"""
        placed_items = {}
        all_item_names = {item['name'] for item in items_data}

        for bin_idx, bin_obj in enumerate(self.packer.bins):
            for item in bin_obj.items:
                if item.name not in placed_items:
                    # 获取位置（py3dbp 的 position 是 Decimal 元组）
                    position = getattr(item, 'position', (0, 0, 0))
                    pos_clean = tuple(
                        round(float(p), 2) if isinstance(p, Decimal)
                        else round(float(p), 2)
                        for p in position
                    )

                    # ✅ 关键修正：使用实际旋转后的尺寸，而不是原始尺寸
                    actual_dims = self._get_actual_dimensions(item)
                    dims_clean = tuple(round(v, 2) for v in actual_dims)

                    placed_items[item.name] = {
                        'bin_index': bin_idx,
                        'position': pos_clean,
                        'dimensions': dims_clean,
                        'rotation_type': getattr(item, 'rotation_type', 0),
                    }

        placed_names = set(placed_items.keys())
        unplaced_names = all_item_names - placed_names

        results = {
            'total_items': len(items_data),
            'placed_count': len(placed_items),
            'unplaced_count': len(unplaced_names),
            'bins': [],
            'unplaced_items': [],
            'placement_summary': {},
        }

        # 整理每个箱子的信息
        for bin_idx, bin_obj in enumerate(self.packer.bins):
            bin_items = []
            for name, info in placed_items.items():
                if info['bin_index'] == bin_idx:
                    bin_items.append({
                        'name': name,
                        'dimensions': info['dimensions'],
                        'position': info['position'],
                        'rotation_type': info['rotation_type'],
                    })

            bin_result = {
                'name': bin_obj.string(),
                'item_count': len(bin_items),
                'items': bin_items,
                'unfitted_count': len(bin_obj.unfitted_items),
                'unfitted_items': [item.name for item in bin_obj.unfitted_items],
            }
            results['bins'].append(bin_result)

        # 未放置物品
        for name in unplaced_names:
            dims = self._get_item_dimensions(name, items_data)
            results['unplaced_items'].append({
                'name': name,
                'dimensions': dims,
            })

        results['placement_summary'] = {
            name: f'箱子{info["bin_index"]+1}'
            for name, info in placed_items.items()
        }

        return results

    def _get_item_dimensions(self, name: str, items_data: List[Dict]) -> Tuple:
        """根据物品名称查找原始尺寸"""
        for item in items_data:
            if item['name'] == name:
                return (item['w'], item['h'], item['d'])
        return (0, 0, 0)