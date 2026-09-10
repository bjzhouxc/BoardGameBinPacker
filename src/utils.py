# src/utils.py
import json
from decimal import Decimal
from typing import Any, Dict


class Formatter:
    """统一格式化工具"""

    @staticmethod
    def round_decimal(value: Any, decimals: int = 1) -> float:
        """安全地将 Decimal 或数值转为保留指定位小数的 float"""
        if value is None:
            return 0.0
        try:
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def format_number(value: Any, decimals: int = 1,
                     show_int_no_decimal: bool = False) -> str:
        """格式化数字为字符串"""
        if value is None:
            return "0"

        try:
            num = float(value)
            if show_int_no_decimal and num == int(num):
                return str(int(num))
            return f"{num:.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def clean_decimal(data: Any, decimals: int = 1) -> Any:
        """递归清理数据中的 Decimal，并保留指定小数位数"""
        if isinstance(data, Decimal):
            return round(float(data), decimals)
        elif isinstance(data, dict):
            return {k: Formatter.clean_decimal(v, decimals) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [Formatter.clean_decimal(v, decimals) for v in data]
        else:
            return data


class ResultPrinter:
    """结果打印和可视化"""

    @staticmethod
    def _convert_decimal(value: Any, keep_decimal: bool = False) -> Any:
        """转换 Decimal 为 float，可选择保留小数位数"""
        if isinstance(value, Decimal):
            float_val = float(value)
            if keep_decimal:
                return round(float_val, 1)
            return float_val
        elif isinstance(value, dict):
            return {k: ResultPrinter._convert_decimal(v, keep_decimal)
                    for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [ResultPrinter._convert_decimal(v, keep_decimal) for v in value]
        else:
            return value

    @staticmethod
    def print_results(results: Dict):
        """打印装箱结果到控制台（保留1位小数）"""
        results = ResultPrinter._convert_decimal(results, keep_decimal=True)

        print("\n" + "=" * 70)
        print("📦 装箱结果统计")
        print("=" * 70)
        print(f"总物品数: {results['total_items']}")
        print(f"✅ 成功放入: {results['placed_count']} 个")
        print(f"❌ 无法放入: {results['unplaced_count']} 个")
        print("=" * 70)

        print("\n📋 各箱子装载详情:")
        print("-" * 70)
        for i, bin_result in enumerate(results['bins'], 1):
            print(f"\n【箱子 {i}】: {bin_result['name']}")
            print(f"  📦 已放入物品数: {bin_result['item_count']}")

            if bin_result.get('items'):
                print("  物品列表:")
                for item in bin_result['items']:
                    dims = item.get('dimensions', (0, 0, 0))
                    pos = item.get('position', (0, 0, 0))
                    print(f"    ✅ {item['name']}: "
                          f"{dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f} "
                          f"(位置: {pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
            else:
                print("    (空)")

        if results.get('unplaced_items'):
            print("\n" + "-" * 70)
            print(f"❌ 所有箱子都无法放入的物品 ({len(results['unplaced_items'])}个):")
            for item in results['unplaced_items']:
                dims = item.get('dimensions', (0, 0, 0))
                print(f"    {item['name']}: {dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f}")

        if results.get('placement_summary'):
            print("\n" + "=" * 70)
            print("📊 放置摘要（物品 → 箱子）:")
            print("-" * 70)
            for name, bin_name in results['placement_summary'].items():
                print(f"  {name} → {bin_name}")
            print("=" * 70)

    @staticmethod
    def save_results(results: Dict, filename: str):
        """保存结果为 JSON"""
        clean_results = ResultPrinter._convert_decimal(results)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到 {filename}")

    @staticmethod
    def export_placement_list(results: Dict, filename: str = 'output/placement.csv'):
        """导出放置清单到 CSV"""
        import csv
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['物品名称', '放置箱子', '长度', '宽度', '高度'])
            for bin_result in results['bins']:
                for item in bin_result['items']:
                    dims = item['dimensions']
                    writer.writerow([
                        item['name'], bin_result['name'],
                        dims[0], dims[1], dims[2]
                    ])
        print(f"✅ 放置清单已导出到 {filename}")