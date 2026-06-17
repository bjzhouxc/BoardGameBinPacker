from src.packer import MyPacker

if __name__ == "__main__":
    myPacker = MyPacker()
    myPacker.add_drawer()
    myPacker.add_items()

    myPacker.pack()
    myPacker.print()