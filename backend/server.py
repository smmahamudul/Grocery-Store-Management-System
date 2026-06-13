
from functools import wraps
import hashlib
import hmac
import json
import os
import secrets

from flask import Flask, jsonify, redirect, request, send_from_directory, session, url_for

import products_dao
import orders_dao
import uom_dao

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI_DIR = os.path.join(BASE_DIR, "ui")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

app = Flask(__name__)
app.secret_key = os.environ.get("GSMS_SECRET_KEY", "gsms-dev-secret-key")


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"sha256${salt}${digest}"


def verify_password(password, stored_value):
    try:
        scheme, salt, digest = stored_value.split("$", 2)
    except ValueError:
        return False
    if scheme != "sha256":
        return False
    expected = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected, digest)


def load_users():
    if not os.path.exists(USERS_FILE):
        default_admin = [{
            "name": "Admin",
            "email": "admin@grocery.com",
            "password_hash": hash_password("admin123")
        }]
        save_users(default_admin)
        return default_admin

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []

    if not any(u.get("email", "").lower() == "admin@grocery.com" for u in users):
        users.append({
            "name": "Admin",
            "email": "admin@grocery.com",
            "password_hash": hash_password("admin123")
        })
        save_users(users)

    return users


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def get_current_user():
    return session.get("user")


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not get_current_user():
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("login_page"))
        return view_func(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return redirect(url_for("dashboard_page") if get_current_user() else url_for("login_page"))


@app.route("/login")
def login_page():
    return send_from_directory(UI_DIR, "login.html")


@app.route("/register")
def register_page():
    return send_from_directory(UI_DIR, "register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/dashboard")
@login_required
def dashboard_page():
    return send_from_directory(UI_DIR, "index.html")


@app.route("/manage-product")
@login_required
def manage_product_page():
    return send_from_directory(UI_DIR, "manage-product.html")


@app.route("/order")
@login_required
def order_page():
    return send_from_directory(UI_DIR, "order.html")


@app.route("/index.html")
def index_html():
    return redirect(url_for("dashboard_page"))


@app.route("/manage-product.html")
def manage_product_html():
    return redirect(url_for("manage_product_page"))


@app.route("/order.html")
def order_html():
    return redirect(url_for("order_page"))


@app.route("/auth/login", methods=["POST"])
def auth_login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    users = load_users()
    user = next((u for u in users if u.get("email", "").lower() == email), None)

    if not user or not verify_password(password, user["password_hash"]):
        return redirect(url_for("login_page", error="Invalid email or password"))

    session["user"] = {"name": user["name"], "email": user["email"]}
    return redirect(url_for("dashboard_page"))


@app.route("/auth/register", methods=["POST"])
def auth_register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password:
        return redirect(url_for("register_page", error="Please complete all fields"))
    if password != confirm_password:
        return redirect(url_for("register_page", error="Passwords do not match"))

    users = load_users()
    if any(u.get("email", "").lower() == email for u in users):
        return redirect(url_for("register_page", error="An account with this email already exists"))

    users.append({
        "name": name,
        "email": email,
        "password_hash": hash_password(password)
    })
    save_users(users)
    session["user"] = {"name": name, "email": email}
    return redirect(url_for("dashboard_page"))


@app.route("/api/me", methods=["GET"])
@login_required
def api_me():
    response = jsonify(get_current_user())
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/getUOM", methods=["GET"])
@login_required
def get_uom():
    response = jsonify(uom_dao.get_uoms(None))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/getProducts", methods=["GET"])
@login_required
def get_products():
    response = jsonify(products_dao.get_all_products(None))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/saveProduct", methods=["POST"])
@login_required
def save_product():
    payload = request.form.get("data")
    request_payload = json.loads(payload) if payload else {}
    product_id = request_payload.get("product_id")

    if product_id and str(product_id) != "0":
        saved_id = products_dao.update_product(None, request_payload)
    else:
        saved_id = products_dao.insert_new_product(None, request_payload)

    response = jsonify({"product_id": saved_id})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/deleteProduct", methods=["POST"])
@login_required
def delete_product():
    return_id = products_dao.delete_product(None, request.form["product_id"])
    response = jsonify({"product_id": return_id})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/getAllOrders", methods=["GET"])
@login_required
def get_all_orders():
    response = jsonify(orders_dao.get_all_orders(None))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/insertOrder", methods=["POST"])
@login_required
def insert_order():
    payload = request.form.get("data")
    request_payload = json.loads(payload) if payload else {}
    order_id = orders_dao.insert_order(None, request_payload)
    response = jsonify({"order_id": order_id})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(os.path.join(UI_DIR, "css"), filename)


@app.route("/js/<path:filename>")
def js_files(filename):
    return send_from_directory(os.path.join(UI_DIR, "js"), filename)


@app.route("/images/<path:filename>")
def image_files(filename):
    return send_from_directory(os.path.join(UI_DIR, "images"), filename)


if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
