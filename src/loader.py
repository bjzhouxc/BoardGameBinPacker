import json
import pandas as pd
from collections import defaultdict

class DataLoader:
    def __init__(self):
        self.drawer = defaultdict(list)
        self.items = defaultdict(list)


    def load_from_excel(self, filepath: str):
        df = pd.read_excel(filepath, sheet_name="data")
        for _, row in df.iterrows():
            type, group = int(row["type"]), int(row["group"])
            if type == 1:
                self.drawer[group].append(
                    (row["name"], float(row["width"]), float(row["height"]), float(row["depth"]), 1000)
                )
            elif type == 2:
                self.items[group].append(
                    (row["name"], float(row["width"]), float(row["height"]), float(row["depth"]), 1)
                )


    def get_drawer(self, group):
        return self.drawer[group]


    def get_items(self, group):
        return self.items[group]