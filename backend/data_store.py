
import json
import os
from copy import deepcopy
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(__file__)
STORE_FILE = os.path.join(BASE_DIR, "store.json")


def _default_store():
    now = datetime.now()
    return {
        "uoms": [
            {"uom_id": 1, "uom_name": "Kg"},
            {"uom_id": 2, "uom_name": "Gram"},
            {"uom_id": 3, "uom_name": "Litre"},
            {"uom_id": 4, "uom_name": "Pack"},
            {"uom_id": 5, "uom_name": "Piece"},
            {"uom_id": 6, "uom_name": "Dozen"},
            {"uom_id": 7, "uom_name": "Bottle"},
            {"uom_id": 8, "uom_name": "Can"},
        ],
        "products": [
            {"product_id": 1, "name": "Rice", "uom_id": 1, "price_per_unit": 65000.0},
            {"product_id": 2, "name": "Milk", "uom_id": 3, "price_per_unit": 2800.0},
            {"product_id": 3, "name": "Eggs", "uom_id": 6, "price_per_unit": 6200.0},
            {"product_id": 4, "name": "Bananas", "uom_id": 1, "price_per_unit": 4500.0},
            {"product_id": 5, "name": "Bread", "uom_id": 4, "price_per_unit": 3200.0},
            {"product_id": 6, "name": "Cooking Oil", "uom_id": 7, "price_per_unit": 23000.0},
            {"product_id": 7, "name": "Tomatoes", "uom_id": 1, "price_per_unit": 3900.0},
            {"product_id": 8, "name": "Soap", "uom_id": 4, "price_per_unit": 5400.0},
        ],
        "orders": [
            {
                "order_id": 1,
                "customer_name": "Kim Minji",
                "total": 77800.0,
                "datetime": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "order_details": [
                    {"product_id": 1, "quantity": 1, "total_price": 65000.0},
                    {"product_id": 2, "quantity": 2, "total_price": 5600.0},
                    {"product_id": 3, "quantity": 1, "total_price": 6200.0},
                    {"product_id": 8, "quantity": 1, "total_price": 5400.0},
                ],
            },
            {
                "order_id": 2,
                "customer_name": "Park Joon",
                "total": 16800.0,
                "datetime": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "order_details": [
                    {"product_id": 4, "quantity": 1, "total_price": 4500.0},
                    {"product_id": 5, "quantity": 2, "total_price": 6400.0},
                    {"product_id": 7, "quantity": 1, "total_price": 3900.0},
                    {"product_id": 8, "quantity": 1, "total_price": 5400.0},
                ],
            },
        ],
        "next_ids": {
            "product_id": 9,
            "order_id": 3,
        },
    }


def _safe_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def load_store():
    if not os.path.exists(STORE_FILE):
        store = _default_store()
        _safe_write(STORE_FILE, store)
        return store

    with open(STORE_FILE, "r", encoding="utf-8") as f:
        try:
            store = json.load(f)
        except json.JSONDecodeError:
            store = _default_store()
            _safe_write(STORE_FILE, store)
            return store

    changed = False
    for key in ("uoms", "products", "orders", "next_ids"):
        if key not in store:
            changed = True
    if changed:
        defaults = _default_store()
        for key, value in defaults.items():
            store.setdefault(key, deepcopy(value))
        _safe_write(STORE_FILE, store)
    return store


def save_store(store):
    _safe_write(STORE_FILE, store)


def get_uom_lookup(store=None):
    store = store or load_store()
    return {int(u["uom_id"]): u["uom_name"] for u in store.get("uoms", [])}


def get_uoms():
    store = load_store()
    return [
        {"uom_id": int(u["uom_id"]), "uom_name": u["uom_name"]}
        for u in sorted(store.get("uoms", []), key=lambda x: int(x["uom_id"]))
    ]


def get_products():
    store = load_store()
    uom_lookup = get_uom_lookup(store)
    products = []
    for p in sorted(store.get("products", []), key=lambda x: int(x["product_id"]), reverse=True):
        products.append({
            "product_id": int(p["product_id"]),
            "name": p["name"],
            "uom_id": int(p["uom_id"]),
            "price_per_unit": float(p["price_per_unit"]),
            "uom_name": uom_lookup.get(int(p["uom_id"]), ""),
        })
    return products


def _normalize_product_payload(product):
    product_name = product.get("product_name") or product.get("name") or ""
    uom_id = int(product.get("uom_id") or 0)
    price_per_unit = float(product.get("price_per_unit") or 0)
    product_id = int(product.get("product_id") or 0)
    return product_name.strip(), uom_id, price_per_unit, product_id


def insert_product(product):
    store = load_store()
    product_name, uom_id, price_per_unit, _ = _normalize_product_payload(product)
    next_id = int(store.setdefault("next_ids", {}).get("product_id", 1))
    new_record = {
        "product_id": next_id,
        "name": product_name,
        "uom_id": uom_id,
        "price_per_unit": price_per_unit,
    }
    store["products"].append(new_record)
    store["next_ids"]["product_id"] = next_id + 1
    save_store(store)
    return next_id


def update_product(product):
    store = load_store()
    product_name, uom_id, price_per_unit, product_id = _normalize_product_payload(product)

    for item in store.get("products", []):
        if int(item["product_id"]) == int(product_id):
            item["name"] = product_name
            item["uom_id"] = uom_id
            item["price_per_unit"] = price_per_unit
            save_store(store)
            return int(product_id)

    raise ValueError("Product not found")


def delete_product(product_id):
    store = load_store()
    product_id = int(product_id)
    products = store.get("products", [])
    store["products"] = [p for p in products if int(p["product_id"]) != product_id]
    save_store(store)
    return product_id


def _product_lookup():
    return {int(p["product_id"]): p for p in load_store().get("products", [])}


def get_order_details(order_id):
    store = load_store()
    product_lookup = _product_lookup()
    for order in store.get("orders", []):
        if int(order["order_id"]) == int(order_id):
            details = []
            for item in order.get("order_details", []):
                product = product_lookup.get(int(item["product_id"]))
                details.append({
                    "order_id": int(order_id),
                    "quantity": float(item["quantity"]),
                    "total_price": float(item["total_price"]),
                    "product_name": product["name"] if product else None,
                    "price_per_unit": float(product["price_per_unit"]) if product else 0.0,
                })
            return details
    return []


def get_all_orders():
    store = load_store()
    orders = []
    for order in sorted(store.get("orders", []), key=lambda x: int(x["order_id"]), reverse=True):
        orders.append({
            "order_id": int(order["order_id"]),
            "customer_name": order["customer_name"],
            "total": float(order["total"]),
            "datetime": order["datetime"],
            "order_details": get_order_details(order["order_id"]),
        })
    return orders


def insert_order(order):
    store = load_store()
    next_id = int(store.setdefault("next_ids", {}).get("order_id", 1))

    customer_name = str(order.get("customer_name", "")).strip()
    order_details = []
    total = 0.0

    for detail in order.get("order_details", []):
        product_id = int(detail.get("product_id") or 0)
        quantity = float(detail.get("quantity") or 0)
        total_price = float(detail.get("total_price") or 0)
        order_details.append({
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price,
        })
        total += total_price

    if not customer_name:
        raise ValueError("Customer name is required")
    if not order_details:
        raise ValueError("At least one product is required")

    total = float(order.get("grand_total") or total)

    store["orders"].append({
        "order_id": next_id,
        "customer_name": customer_name,
        "total": total,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "order_details": order_details,
    })
    store["next_ids"]["order_id"] = next_id + 1
    save_store(store)
    return next_id
