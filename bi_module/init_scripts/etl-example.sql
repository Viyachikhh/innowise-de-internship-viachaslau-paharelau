

COPY stage.super_store (row_id, order_id, order_date, ship_date, 
                        ship_mode, customer_id, customer_name,
                        segment, country, city, _state, postal_code, 
                        region, product_id, category, sub_category, 
                        product_name, sales, quantity, discount, profit)
FROM '/file_storage/original_data.csv'
WITH (
    FORMAT csv,      -- указываем формат
    HEADER true,     -- пропускаем первую строку (заголовок)
    DELIMITER ','    -- разделитель (обычно запятая)
);

CALL stage.from_stage_to_core();



COPY stage.super_store (row_id, order_id, order_date, ship_date, 
                        ship_mode, customer_id, customer_name,
                        segment, country, city, _state, postal_code, 
                        region, product_id, category, sub_category, 
                        product_name, sales, quantity, discount, profit)
FROM '/file_storage/dcp1.csv'
WITH (
    FORMAT csv,      -- указываем формат
    HEADER true,     -- пропускаем первую строку (заголовок)
    DELIMITER ','    -- разделитель (обычно запятая)
);

CALL stage.from_stage_to_core();




COPY stage.super_store (row_id, order_id, order_date, ship_date, 
                        ship_mode, customer_id, customer_name,
                        segment, country, city, _state, postal_code, 
                        region, product_id, category, sub_category, 
                        product_name, sales, quantity, discount, profit)
FROM '/file_storage/dcp2.csv'
WITH (
    FORMAT csv,      -- указываем формат
    HEADER true,     -- пропускаем первую строку (заголовок)
    DELIMITER ','    -- разделитель (обычно запятая)
);

CALL stage.from_stage_to_core();
