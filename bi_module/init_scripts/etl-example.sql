

COPY stage.super_store (row_id, order_uniq_card, order_date, ship_date, 
                        ship_mode, customer_uniq_card, customer_name,
                        segment, country, city, _state, postal_code, 
                        region, product_uniq_card, category, sub_category, 
                        product_name, sales, quantity, discount, profit)
FROM '/file_storage/original_data.csv'
WITH (
    FORMAT csv,      -- указываем формат
    HEADER true,     -- пропускаем первую строку (заголовок)
    DELIMITER ','    -- разделитель (обычно запятая)
);

CALL stage.from_stage_to_core_v2();



COPY stage.super_store (row_id, order_uniq_card, order_date, ship_date, 
                        ship_mode, customer_uniq_card, customer_name,
                        segment, country, city, _state, postal_code, 
                        region, product_uniq_card, category, sub_category, 
                        product_name, sales, quantity, discount, profit)
FROM '/file_storage/secondary_data.csv'
WITH (
    FORMAT csv,      
    HEADER true,     
    DELIMITER ',' 
);

CALL stage.from_stage_to_core_v2();



----------- в mart слой
CALL core.update_mart();