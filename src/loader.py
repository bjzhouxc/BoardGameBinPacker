# src/loader.py
import json
import csv
import pandas as pd
from typing import List, Dict, Tuple
from pathlib import Path


class DataLoader:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)

    # ==================== JSON 加载 ====================

    def load_items_from_json(self, filename: str) -> List[Dict]:
        """从JSON加载物品数据"""
        filepath = self.data_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'items' in data:
            items_data = data['items']
        elif isinstance(data, list):
            items_data = data
        else:
            if all(key in data for key in ['name', 'width', 'height', 'depth']):
                items_data = [data]
            else:
                raise ValueError("无法识别的JSON格式")

        return [self._format_item(item) for item in items_data]

    def load_bins_from_json(self, filename: str) -> List[Tuple[float, float, float]]:
        """从JSON加载箱子尺寸"""
        filepath = self.data_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'bins' in data:
            bins_data = data['bins']
        elif isinstance(data, list) and all(
            'width' in b or 'dimensions' in b for b in data
        ):
            bins_data = data
        else:
            raise ValueError("无法识别的JSON格式")

        formatted_bins = []
        for bin_item in bins_data:
            if 'width' in bin_item and 'height' in bin_item and 'depth' in bin_item:
                formatted_bins.append((
                    float(bin_item['width']),
                    float(bin_item['height']),
                    float(bin_item['depth'])
                ))
            elif 'dimensions' in bin_item and len(bin_item['dimensions']) == 3:
                formatted_bins.append(tuple(float(d) for d in bin_item['dimensions']))
            else:
                raise ValueError(f"无法识别的箱子格式: {bin_item}")

        return formatted_bins

    def load_full_json(self, filename: str) -> Dict:
        """一次性加载完整的JSON数据"""
        filepath = self.data_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        result = {'items': [], 'bins': [], 'config': {}}

        if 'items' in data:
            result['items'] = [self._format_item(item) for item in data['items']]

        if 'bins' in data:
            for bin_item in data['bins']:
                if 'width' in bin_item and 'height' in bin_item and 'depth' in bin_item:
                    result['bins'].append((
                        float(bin_item['width']),
                        float(bin_item['height']),
                        float(bin_item['depth'])
                    ))
                elif 'dimensions' in bin_item and len(bin_item['dimensions']) == 3:
                    result['bins'].append(tuple(float(d) for d in bin_item['dimensions']))

        if 'config' in data:
            result['config'] = data['config']

        return result

    def _format_item(self, item: Dict) -> Dict:
        """统一格式化物品数据"""
        name = item.get('name') or item.get('id') or f"物品_{item.get('id', 'unknown')}"

        if 'width' in item and 'height' in item and 'depth' in item:
            w, h, d = float(item['width']), float(item['height']), float(item['depth'])
        elif 'dimensions' in item and len(item['dimensions']) == 3:
            w, h, d = (float(item['dimensions'][0]),
                       float(item['dimensions'][1]),
                       float(item['dimensions'][2]))
        else:
            raise ValueError(f"物品 {name} 缺少尺寸信息")

        weight = float(item.get('weight', 1))

        return {'name': name, 'w': w, 'h': h, 'd': d, 'weight': weight}

    # ==================== CSV / Excel 加载 ====================

    def load_items_from_csv(self, filename: str) -> List[Dict]:
        """从CSV加载物品数据"""
        filepath = self.data_dir / filename
        items = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append({
                    'name': row['name'],
                    'w': float(row['width']),
                    'h': float(row['height']),
                    'd': float(row['depth']),
                    'weight': float(row.get('weight', 1))
                })
        return items

    def load_items_from_excel(self, filename: str, sheet_name: str = 'Sheet1') -> List[Dict]:
        """从Excel加载物品数据"""
        filepath = self.data_dir / filename
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        items = []
        for _, row in df.iterrows():
            items.append({
                'name': row['name'],
                'w': float(row['width']),
                'h': float(row['height']),
                'd': float(row['depth']),
                'weight': float(row.get('weight', 1))
            })
        return items

    def load_bin_dimensions(self, filename: str) -> List[Tuple[float, float, float]]:
        """加载箱子尺寸（从CSV）"""
        filepath = self.data_dir / filename
        bins = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                bins.append((
                    float(row['width']),
                    float(row['height']),
                    float(row['depth'])
                ))
        return bins