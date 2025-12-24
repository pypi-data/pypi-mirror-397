from pathlib import Path
from .speakers import Thomas

def main():
    Thomas().print_name()
    # with open("names.txt") as f:
    print(__file__)
    with (Path(__file__).parent / "names.txt").open() as f:
        print(f.read())

if __name__ == "__main__":
    main()