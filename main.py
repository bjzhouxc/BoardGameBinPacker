# main.py
import os
import sys

# 确保项目根目录在 Python 路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.packer import ThreeDBoxPacker
from src.loader import DataLoader
from src.utils import ResultPrinter
from src.visualizer import BinVisualizer


def main():
    # 1. 加载数据
    print("📂 正在加载数据...")
    loader = DataLoader('data')
    data = loader.load_full_json('packing_data.json')

    bin_dims = data['bins']
    items = data['items']
    config = data['config']

    print(f"✅ 加载完成: {len(bin_dims)} 个箱子, {len(items)} 个物品")

    # 2. 执行装箱
    print("\n🔧 正在执行装箱算法...")
    bigger_first = config.get('bigger_first', True)
    packer = ThreeDBoxPacker(bin_dims)
    results = packer.pack_items(items, bigger_first=bigger_first)

    # 3. 打印结果
    printer = ResultPrinter()
    printer.print_results(results)

    # 4. 保存结果 JSON
    output_file = config.get('output_file', 'output/results.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    printer.save_results(results, output_file)

    # 5. 3D 可视化
    print("\n🎨 正在生成 3D 可视化图...")
    bins_items = [bin_result['items'] for bin_result in results['bins']]

    visualizer = BinVisualizer(bin_size=bin_dims[0])
    visualizer.visualize_all_bins(
        bins_data=bins_items,
        bin_sizes=bin_dims,
        title_prefix='箱子',
        save_dir='output/figures'
    )

    print("\n✅ 全部完成！")


if __name__ == '__main__':
    main()