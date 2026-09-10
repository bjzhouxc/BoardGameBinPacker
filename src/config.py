# src/config.py
from dataclasses import dataclass


@dataclass
class PackingConfig:
    """装箱配置"""
    bigger_first: bool = True          # 是否优先放大物品
    max_weight: float = 1000           # 箱子最大承重
    distribute_items: bool = False     # 是否分散装箱

    # 文件路径配置
    items_file: str = 'items.csv'
    bins_file: str = 'bins.csv'

    # 输出配置
    output_format: str = 'print'
    output_file: str = 'output/results.json'


# 预设配置方案
config_quantity = PackingConfig(bigger_first=True)    # 最大化数量
config_volume = PackingConfig(bigger_first=False)     # 最大化体积利用率