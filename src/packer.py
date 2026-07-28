from py3dbp import Packer, Bin, Item

class MyPacker:
    def __init__(self):
        self.packer = Packer()
        self.item_cnt = 0


    def add_drawer(self, drawers):
        for name, w, h, d, weight in drawers:
            self.packer.add_bin(Bin(name, w, h, d, weight))


    def add_items(self, items):
        for name, w, h, d, weight in items:
            self.packer.add_item(Item(name, w, h, d, weight))
            self.item_cnt += 1


    def pack(self):
        self.packer.pack(bigger_first=True, distribute_items=True)


    def print(self):
        total_packed = 0
        for bin in self.packer.bins:
            print(f"\n========== {bin.string()} ==========")
            for item in bin.items:
                # print(f"  - {item.string()}")
                w, h, d = item.get_dimension()
                x, y, z = item.position
                print(f"  - {item.name} ({x:.1f}, {y:.1f}, {z:.1f}) + ({w:.1f}, {h:.1f}, {d:.1f})")
            total_packed += len(bin.items)

        print(f"Packed items: {total_packed} / {self.item_cnt}")


    def plot(self):
        pass