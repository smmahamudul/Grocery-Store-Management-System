# Grocery Store Management System

This version keeps the grocery product and order features and includes working register/login pages.

## What is included

- Dashboard with summary cards and recent orders
- Products page with add, edit, and delete
- New order page with validation and automatic totals
- Login and register pages
- Session-based access control
- Preloaded products and sample orders
- Default demo admin account

## Default demo login

- Email: `admin@grocery.com`
- Password: `admin123`

## Setup

### 1) Install dependencies

```bash
pip install flask
```

### 2) Run the backend

From the `backend` folder:

```bash
python server.py
```

### 3) Open the app

Go to:

- `http://127.0.0.1:5000`

## Notes

- The app uses local JSON storage
- Register creates a new user in `backend/users.json`
- Login is required before opening the dashboard, products, or order pages
- The UI assets are served by Flask, so use the backend URL instead of opening the HTML files directly
