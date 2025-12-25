CREATE OR REPLACE PROCEDURE stage.from_stage_to_core()
LANGUAGE plpgsql
AS $$
BEGIN


    ----------------------------- core.products
    MERGE INTO core.products dest
    USING (
        SELECT DISTINCT product_id, category, sub_category, product_name, sales, quantity
        FROM stage.super_store
    ) src
    ON src.product_id = dest.product_uniq_card
            
    WHEN NOT MATCHED THEN
        INSERT (product_uniq_card, category, sub_category, product_name, sales, quantity)
        VALUES (src.product_id, src.category, src.sub_category, src.product_name, src.sales, src.quantity);
    ------------------------------------------

    
    ----------------------------- core.orders
    MERGE INTO core.orders dest
    USING (
        SELECT DISTINCT order_id, order_date, ship_date, ship_mode
        FROM stage.super_store
    ) src
    ON src.order_id = dest.order_uniq_card
            
    WHEN NOT MATCHED THEN
        INSERT (order_uniq_card, order_date, ship_date, ship_mode)
        VALUES (src.order_id, src.order_date, src.ship_date, src.ship_mode);
    ------------------------------------------


    ----------------------------- core.customers
    --таблица для (по)перехавших пользователей
    CREATE TEMP TABLE core.moved_customers ( LIKE core.customers ) ;
    
    --вставка данных в таблицу
    INSERT INTO core.moved_customers (customer_uniq_card, customer_name, 
                                        segment, country, city, 
                                        _state, postal_code, region, 
                                        is_active, updated_at)
    
    SELECT DISTINCT customer_id, customer_name, 
                    segment, country, city, 
                    _state, postal_code, region, 
                    is_active, updated_at 
                    FROM stage.super_store ss
                    WHERE ss.customer_id IN (SELECT cc.order_uniq_card from core.customers cc) AND 
                    (ss.customer_id, ss.region) NOT IN (SELECT cc.order_uniq_card, cc.region from core.customers cc);
    --SCD Type 2
    --обновление пользователей, которые переехали из старого региона
    UPDATE core.customers cc
    SET cc.is_active = FALSE
    WHERE cc.customer_uniq_card IN (select t.customer_uniq_card from core.moved_customers t) AND 
    (cc.customer_uniq_card, cc.region) NOT IN (select t.customer_uniq_card, t.region from core.moved_customers t) AND cc.is_active = TRUE;

    --добавление пользователей, которые переехали, уже с новым регионом
    INSERT INTO core.customers (customer_uniq_card, customer_name, 
                                        segment, country, city, 
                                        _state, postal_code, region, 
                                        is_active, updated_at)
    SELECT * FROM core.moved_customers;

    --остальные случаи
    MERGE INTO core.customers dest
    USING (
        SELECT DISTINCT customer_id, customer_name, 
                    segment, country, city, 
                    _state, postal_code, region, 
                    is_active, updated_at 
                    FROM stage.super_store 
        EXCEPT
        SELECT * FROM core.moved_customers
    ) src
    ON src.customer_id = dest.order_uniq_card

    --полный matched ничего не делает, т.е. если все данные совпадают

    --смена имени SCD Type 1
    WHEN MATCHED AND dest.customer_name IS DISTINCT FROM src.customer_name THEN
        UPDATE 
        SET dest.customer_name = src.customer_name
            
    --новые данные
    WHEN NOT MATCHED THEN
        INSERT (order_uniq_card, customer_name, segment, country, city, _state, postal_code, region, is_active, updated_at)
        VALUES (src.order_uniq_card, src.customer_name, src.segment, 
                src.country, src.city, src._state, 
                src.postal_code, src.region, 
                TRUE, NOW());
    --------------------------------------------------

    ----------------------------- core.sales
    MERGE INTO core.sales dest
    USING (
        SELECT DISTINCT ss.row_id, co.order_id, cc.customer_id, cp.product_id, ss.discount, ss.profit
        FROM stage.super_store ss
        INNER JOIN core.orders co ON co.order_uniq_card=ss.order_id AND
                                     co.order_date=ss.order_date AND 
                                     co.ship_date=ss.ship_date AND 
                                     co.ship_mode=ss.ship_mode
        INNER JOIN core.products cp ON cp.product_uniq_card=ss.product_id AND 
                                    cp.category=ss.category AND 
                                    cp.sub_category=ss.sub_category AND
                                    cp.product_name=ss.product_name AND
                                    cp.sales=ss.sales AND
                                    cp.quantity=ss.quantity
        INNER JOIN core.customers cc ON cc.customer_uniq_card=ss.customer_id AND 
                                    cc.customer_name=ss.customer_name AND 
                                    cc.segment=ss.segment AND
                                    cc.country=ss.country AND
                                    cc.city=ss.city AND
                                    cc._state=ss._state AND
                                    cc.postal_code=ss.postal_code AND
                                    cc.region=ss.region
        WHERE cc.is_active = TRUE                           
    ) src
    ON src.row_id = dest.sale_id

    WHEN NOT MATCHED THEN
        INSERT (sale_id, order_id, customer_id, product_id, discount, profit)
        VALUES (src.row_id, src.order_id, src.customer_id, src.product_id, src.discount, src.profit);

    DROP TABLE core.moved_customers;
    TRUNCATE TABLE stage.super_store;


EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Ошибка при обновлении товара ID %: %', p_id, SQLERRM;
END;
$$;