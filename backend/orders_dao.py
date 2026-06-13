
from data_store import get_all_orders as _get_all_orders
from data_store import insert_order as _insert_order


def insert_order(connection, order):
    return _insert_order(order)


def get_order_details(connection, order_id):
    all_orders = _get_all_orders()
    for order in all_orders:
        if int(order["order_id"]) == int(order_id):
            return order.get("order_details", [])
    return []


def get_all_orders(connection):
    return _get_all_orders()


if __name__ == "__main__":
    print(get_all_orders())
