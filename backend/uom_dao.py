
from data_store import get_uoms as _get_uoms


def get_uoms(connection=None):
    return _get_uoms()


if __name__ == "__main__":
    print(get_uoms())
