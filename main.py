from src.packer import MyPacker
from src.loader import DataLoader

if __name__ == "__main__":
    myPacker = MyPacker()
    myLoader = DataLoader()

    myLoader.load_from_excel("data/data.xlsx")
    myPacker.add_drawer(myLoader.get_drawer(1))
    myPacker.add_items(myLoader.get_items(1))

    myPacker.pack()
    myPacker.print()