from py3dbp import Packer, Bin, Item

class MyPacker:
    def __init__(self):
        self.packer = Packer()
        self.items_data = []


    def add_drawer(self):
        self.packer.add_bin(Bin("Drawer1", 28, 34.5, 15, 1000))
        self.packer.add_bin(Bin("Drawer2", 28, 34.5, 15, 1000))
        # self.packer.add_bin(Bin("CompanyDrawer1", 31, 38, 11, 1000))
        # self.packer.add_bin(Bin("CompanyDrawer1", 31, 38, 25, 1000))


    def add_items(self):
        # self.items_data = [
        #     ("作弊飞蛾", 11.5, 11.5, 3.5, 1),
        #     ("德国心脏病", 13, 17, 6, 1),
        #     ("犯人在跳舞", 13, 14, 3, 1),
        #     ("还玩好游戏", 11, 15.5, 4, 1),
        #     ("三国杀: 诸侯讨董", 15, 20, 3, 1),
        #     ("赎罪之旅", 10, 14, 3.5, 1),
        #     ("Leet Poker", 9, 12, 3, 1),
        #     ("赌命大赛", 15, 15, 7, 1),
        #     ("红色的门与杀人鬼的钥匙", 8, 10.5, 3, 1),
        #     ("三国杀王者之战", 9, 13, 3.5, 1),
        #     ("瞎掰王", 10, 15, 5, 1),
        #     ("猩猩相惜", 10, 15, 5, 1),
        #     ("德国蟑螂", 11, 11, 3.5, 1),
        #     ("小黑屋：第三版", 27, 27, 8.5, 1)
        # ]
        self.items_data = [
            ("血与刃的白蔷薇", 14.5, 14.5, 5.0, 1),
            ("行动代号", 23.2, 16.2, 5.0, 1),
            ("鲜血盟约", 20.4, 20.4, 3.0, 1),
            ("暑假日记", 15.5, 10.2, 4.6, 1),
            ("屁者先知", 13.9, 13.2, 6.9, 1),
            ("一夜终极狼人", 17.5, 13.4, 3.8, 1),
            ("骇浪求生", 19.6, 10.4, 3.6, 1),
            ("冰冷的她醒来之前", 10.4, 9.0, 2.5, 1),
            ("两室一弹", 20.3, 14.3, 4.0, 1),
            ("炸弹猫: 灾厄菜谱", 30.5, 20.8, 7.8, 1),
            ("情书", 10.2, 14.2, 3.3, 1)
        ]

        for name, w, h, d, weight in self.items_data:
            self.packer.add_item(Item(name, w, h, d, weight))


    def pack(self):
        self.packer.pack(bigger_first=True, distribute_items=True)


    def print(self):
        total_packed = 0
        for bin in self.packer.bins:
            print(f"\n========== {bin.string()} ==========")
            for item in bin.items:
                # print(f"  - {item.string()}")
                w, h, d = item.get_dimension()
                print(f"  - {item.name} ({w}, {h}, {d}) pos: {item.position}")
            total_packed += len(bin.items)

        print(f"Packed items: {total_packed} / {len(self.items_data)}")