from py3dbp import Packer, Bin, Item

class MyPacker:
    def __init__(self):
        self.packer = Packer()
        self.item_cnt = 0


    def add_drawer(self, drawers):
        for name, w, h, d, weight in drawers:
            self.packer.add_bin(Bin(name, w, h, d, weight))


    def add_items(self, items):
        # self.items_data = [
        #     ("作弊飞蛾", 11.5, 11.5, 3.5, 1),
        #     ("德国心脏病", 13, 17, 6, 1),
        #     ("犯人在跳舞", 13, 14, 3, 1),
        #     ("还玩好游戏", 11, 15.5, 4, 1),
        #     ("三国杀: 诸侯讨董", 15, 20, 3, 1),
        #     ("Leet Poker", 9, 12, 3, 1),
        #     ("赌命大赛", 15, 15, 7, 1),
        #     ("三国杀王者之战", 9, 13, 3.5, 1),
        #     ("瞎掰王", 10, 15, 5, 1),
        #     ("猩猩相惜", 10, 15, 5, 1),
        #     ("德国蟑螂", 11, 11, 3.5, 1),
        #     ("小黑屋：第三版", 27, 27, 8.5, 1)
        # ]
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