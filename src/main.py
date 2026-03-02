from src.setup import setup
from src.config import DATABASE_PATH


def main():
    setup(DATABASE_PATH.absolute().as_posix())


if __name__ == "__main__":
    main()
