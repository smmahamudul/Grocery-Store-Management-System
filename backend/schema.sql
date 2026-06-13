CREATE DATABASE IF NOT EXISTS grocery_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE grocery_store;

CREATE TABLE IF NOT EXISTS uom (
    uom_id INT AUTO_INCREMENT PRIMARY KEY,
    uom_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    uom_id INT NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_products_uom
        FOREIGN KEY (uom_id) REFERENCES uom(uom_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    datetime DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_details_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_order_details_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

INSERT IGNORE INTO uom (uom_name) VALUES
('Kg'), ('Gram'), ('Litre'), ('Pack'), ('Piece'), ('Dozen');
