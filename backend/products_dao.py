
from data_store import delete_product as _delete_product
from data_store import get_products as _get_products
from data_store import insert_product as _insert_product
from data_store import update_product as _update_product


def get_all_products(connection=None):
    return _get_products()


def insert_new_product(connection, product):
    return _insert_product(product)


def update_product(connection, product):
    return _update_product(product)


def delete_product(connection, product_id):
    return _delete_product(product_id)


if __name__ == "__main__":
    print(get_all_products())
