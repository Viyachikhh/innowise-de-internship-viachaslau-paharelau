--USE postgres;

---------схемы базы--------------------------------------------------------
---------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS stage;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS mart;

---------stage слой--------------------------------------------------------
---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS stage.super_store (
    row_id SERIAL,
    order_id VARCHAR(20),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(25),
    customer_id CHAR(8),
    customer_name VARCHAR(100),
    segment VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    _state VARCHAR(100),
    postal_code VARCHAR(5),
    region VARCHAR(100),
    product_id CHAR(15),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(200),
    sales DECIMAL(10, 4),
    quantity INT,
    discount DECIMAL(3, 2),
    profit DECIMAL(10, 4)
);

---------core слой---------------------------------------------------------
---------------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS core.customers (
    customer_id SERIAL,
    customer_uniq_card CHAR(8),
    customer_name VARCHAR(100),
    segment VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    _state VARCHAR(100),
    postal_code VARCHAR(5),
    region VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(customer_id)
);


CREATE TABLE IF NOT EXISTS core.orders (
    order_id SERIAL,
    order_uniq_card VARCHAR(20),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(25),
    PRIMARY KEY(order_id)
    --UNIQUE (order_uniq_card)
);


CREATE TABLE IF NOT EXISTS core.products (
    product_id SERIAL,
    product_uniq_card CHAR(15),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(200),
    sales DECIMAL(10, 4),
    quantity INT,
    PRIMARY KEY(product_id)
    --UNIQUE (product_uniq_card)
);


--основная таблица
CREATE TABLE IF NOT EXISTS core.sales (
    sale_id SERIAL,
    order_id SERIAL,
    customer_id SERIAL,
    product_id SERIAL,
    discount DECIMAL(3, 2),
    profit DECIMAL(10, 4),
    PRIMARY KEY(sale_id),
    CONSTRAINT fk_sales_orders FOREIGN KEY (order_id) REFERENCES CORE.orders(order_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_sales_customers FOREIGN KEY (customer_id) REFERENCES CORE.customers(customer_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_sales_products FOREIGN KEY (product_id) REFERENCES CORE.products(product_id) ON DELETE SET NULL ON UPDATE CASCADE
);



---------mart слой---------------------------------------------------------
---------------------------------------------------------------------------

--денормализированная звезда
CREATE TABLE IF NOT EXISTS mart.fact_sales (
    sale_id SERIAL,
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(25),
    customer_name VARCHAR(100),
    segment VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    _state VARCHAR(100),
    postal_code VARCHAR(5),
    region VARCHAR(100),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(200),
    sales DECIMAL(10, 4),
    quantity INT,
    discount DECIMAL(3, 2),
    profit DECIMAL(10, 4)
);