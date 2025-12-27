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
    CREATE TEMP TABLE scd2 ( LIKE core.customers INCLUDING DEFAULTS) ;
    --SELECT customer_id from scd2 limit 1;
    --вставка данных в таблицу
    INSERT INTO scd2 (customer_uniq_card, customer_name, 
                                        segment, country, city, 
                                        _state, postal_code, region, 
                                        is_active, updated_at)
    
    SELECT DISTINCT ss.customer_id, ss.customer_name, 
                    ss.segment, ss.country, ss.city, 
                    ss._state, ss.postal_code, ss.region, 
                    TRUE, NOW() 
                    FROM stage.super_store ss
                    WHERE ss.customer_id IN (SELECT cc.customer_uniq_card from core.customers cc) AND 
                    (ss.customer_id, ss.region) NOT IN (SELECT cc.customer_uniq_card, cc.region from core.customers cc);

    --если так получилось, что в поток попали изменения одного и того же человека, возьмётся последняя запись о нём
    UPDATE scd2
    set is_active = FALSE
    WHERE (customer_uniq_card, region) NOT IN (SELECT s21.customer_uniq_card, s21.region FROM 
                                            (SELECT customer_uniq_card, region FROM scd2) s21 INNER JOIN 
                                            (SELECT ROW_NUMBER() OVER (PARTITION BY customer_uniq_card 
                                                                        ORDER BY customer_id DESC) as rn, 
                                                                        customer_uniq_card, 
                                                                        region FROM scd2) s22
                                            ON s21.customer_uniq_card=s22.customer_uniq_card AND s21.region=s22.region
                                            WHERE s22.rn = 1);
    --SCD Type 2
    --обновление пользователей, которые переехали из старого региона
    UPDATE core.customers cc
    SET is_active = FALSE
    WHERE cc.customer_uniq_card IN (select t.customer_uniq_card from scd2 t) AND 
    (cc.customer_uniq_card, cc.region) NOT IN (select t.customer_uniq_card, t.region from scd2 t) AND cc.is_active = TRUE;

    --добавление пользователей, которые переехали, уже с новым регионом
    INSERT INTO core.customers (customer_uniq_card, customer_name, 
                                        segment, country, city, 
                                        _state, postal_code, region, 
                                        is_active, updated_at)
    SELECT customer_uniq_card, customer_name, 
            segment, country, city, _state, 
            postal_code, region, is_active, updated_at FROM scd2;

    --остальные случаи
    MERGE INTO core.customers dest
    USING (
        SELECT DISTINCT customer_id as customer_uniq_card, customer_name, 
                    segment, country, city, 
                    _state, postal_code, region, 
                    TRUE, NOW() 
                    FROM stage.super_store 
        EXCEPT
        SELECT customer_uniq_card, customer_name, 
                    segment, country, city, 
                    _state, postal_code, region, 
                    TRUE, NOW() 
                    FROM scd2
    ) src
    ON src.customer_uniq_card = dest.customer_uniq_card

    --полный matched ничего не делает, т.е. если все данные совпадают

    --смена имени SCD Type 1
    WHEN MATCHED AND dest.customer_name IS DISTINCT FROM src.customer_name THEN
        UPDATE 
        SET customer_name = src.customer_name
            
    --новые данные
    WHEN NOT MATCHED THEN
        INSERT (customer_uniq_card, customer_name, segment, country, city, _state, postal_code, region, is_active, updated_at)
        VALUES (src.customer_uniq_card, src.customer_name, src.segment, 
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

    WHEN MATCHED AND dest.customer_id IS DISTINCT FROM src.customer_id THEN
        UPDATE 
        SET customer_id = src.customer_id

    WHEN NOT MATCHED THEN
        INSERT (sale_id, order_id, customer_id, product_id, discount, profit)
        VALUES (src.row_id, src.order_id, src.customer_id, src.product_id, src.discount, src.profit);

    DROP TABLE scd2;
    TRUNCATE TABLE stage.super_store;
END;
$$;






CREATE OR REPLACE PROCEDURE stage.from_stage_to_core_v2()
LANGUAGE plpgsql
AS $$
BEGIN

    -------------------------------------------------
    ------- product_categories, customers и locations
    --обработки dcp1 для списков товаров нет необходимости, т.к. в датасете есть товары с одинаковыми product_id, но разными именами
    -----product_categories
    MERGE INTO core.product_categories dest
        USING (
            SELECT DISTINCT product_uniq_card, category, sub_category FROM stage.super_store
        ) src
        ON src.product_uniq_card=dest.product_uniq_card AND 
           src.category=dest.category AND
           src.sub_category=dest.sub_category 

        --новые
        WHEN NOT MATCHED THEN 
            INSERT (product_uniq_card, category, sub_category)
            VALUES (src.product_uniq_card, src.category, src.sub_category); 


    ---locations
    MERGE INTO core.locations dest
        USING (
            SELECT DISTINCT country, city, _state, postal_code, region FROM stage.super_store
        ) src
        ON src.country=dest.country AND src.city=dest.city AND
            src._state=dest._state AND src.postal_code=dest.postal_code AND 
            src.region=dest.region

        WHEN NOT MATCHED THEN 
            INSERT (country, city, _state, postal_code, region)
            VALUES (src.country, src.city, src._state, src.postal_code, src.region);


    --customers
    MERGE INTO core.customers dest
        USING (
            SELECT DISTINCT customer_uniq_card, customer_name, segment FROM stage.super_store
        ) src
        ON src.customer_uniq_card=dest.customer_uniq_card

        --dcp1
        WHEN MATCHED AND (src.customer_name, src.segment) IS DISTINCT FROM (dest.customer_name, dest.segment) THEN
            UPDATE
            SET customer_name=src.customer_name, segment=src.segment
        --новые
        WHEN NOT MATCHED THEN 
            INSERT (customer_uniq_card, customer_name, segment)
            VALUES (src.customer_uniq_card, src.customer_name, src.segment);
    -------------------------------------------------

    --/*

    -------------------------------------------------
    ------- product_entities 
    -- пока никакую логику относительно DCP1/DCP2
    -- выполнять не нужно, поэтому просто merge 
    MERGE INTO core.product_entities dest
        USING (
            SELECT DISTINCT cpc.product_uniq_card, ss.product_name, ss.sales, ss.quantity 
            FROM stage.super_store ss
            INNER JOIN core.product_categories cpc ON ss.product_uniq_card=cpc.product_uniq_card
        ) src
        ON src.product_uniq_card=dest.product_uniq_card AND src.product_name=dest.product_name

        WHEN NOT MATCHED THEN 
            INSERT (product_uniq_card, product_name, sales, quantity)
            VALUES (src.product_uniq_card, src.product_name, src.sales, src.quantity);
    -------------------------------------------------


    
    -------------------------------------------------
    ------- customer_accounts 

    -- временная таблица для dcp2
    CREATE TEMP TABLE scd2 (LIKE core.customer_accounts INCLUDING ALL);

    -- заполнение теми записями, пары которых нет в customer_account
    -- последний вложенный запрос, если мы хотим, чтобы триггерилось 
    -- только от изменения region
    INSERT INTO scd2 (customer_id, location_id, is_active, updated_at)
    SELECT DISTINCT cc.id, cl.id, TRUE, NOW() + INTERVAL '1 MINUTE' 
    FROM stage.super_store ss 
    INNER JOIN core.customers cc ON ss.customer_uniq_card=cc.customer_uniq_card --AND 
                                    --ss.customer_name=cc.customer_name AND
                                    --ss.segment=cc.segment
    INNER JOIN core.locations cl ON ss.country=cl.country AND ss.city=cl.city AND 
                                    ss._state=cl._state AND ss.postal_code=cl.postal_code AND 
                                    ss.region=cl.region
    WHERE (cc.id, cl.id) NOT IN (
        SELECT customer_id, location_id FROM core.customer_accounts
    ) AND (cl.country, cl.city, cl._state, cl.postal_code) IN (
        SELECT country, city, _state, postal_code FROM core.locations
    );


    --логика смены статуса (по)переехавшего пользователя (SCD2)
    --если так получилось, что в поток попали изменения одного и того же человека, возьмётся последняя запись о нём
    UPDATE scd2
    set is_active = FALSE
    WHERE (customer_id, location_id) NOT IN (SELECT s21.customer_id, s21.location_id FROM 
                                            (SELECT customer_id, location_id FROM scd2) s21 INNER JOIN 
                                            (SELECT ROW_NUMBER() OVER (PARTITION BY customer_id 
                                                                        ORDER BY location_id DESC, id desc) as row_num, 
                                                                        customer_id, 
                                                                        location_id FROM scd2) s22
                                            ON s21.customer_id=s22.customer_id AND s21.location_id=s22.location_id
                                            WHERE s22.row_num = 1);

    --вставка scd2 пользователей
    INSERT INTO core.customer_accounts (customer_id, location_id, is_active, updated_at)
    SELECT DISTINCT customer_id, location_id, is_active, updated_at FROM scd2;

    --сделать неактивными тех, кто переехал
    UPDATE core.customer_accounts cca
    SET is_active = FALSE
    WHERE cca.customer_id IN (select t.customer_id from scd2 t) AND 
    (cca.customer_id, cca.location_id) NOT IN (select t.customer_id, t.location_id from scd2 t) AND cca.is_active = TRUE;
    

    ---для новых customer_accounts
    MERGE INTO core.customer_accounts dest
        USING (
            SELECT DISTINCT cc.id as customer_id, cl.id as location_id, 
                            TRUE as is_active, NOW() + INTERVAL '1 MINUTE' as updated_at
            FROM stage.super_store ss 
            INNER JOIN core.customers cc ON ss.customer_uniq_card=cc.customer_uniq_card
            INNER JOIN core.locations cl ON ss.country=cl.country AND ss.city=cl.city AND 
                                            ss._state=cl._state AND ss.postal_code=cl.postal_code AND 
                                            ss.region=cl.region

                EXCEPT 

            SELECT customer_id, location_id, is_active, updated_at FROM scd2
        ) src
        ON src.customer_id=dest.customer_id AND src.location_id=dest.location_id


        WHEN NOT MATCHED THEN 
            INSERT (customer_id, location_id, is_active, updated_at)
            VALUES (src.customer_id, src.location_id, src.is_active, src.updated_at);
    ---------------------------------------------------------


    ---------------------------------------------------------
    ----- orders
    MERGE INTO core.orders dest
        USING (
            SELECT DISTINCT order_uniq_card, order_date, ship_date, ship_mode 
            FROM stage.super_store
        ) src
        ON src.order_uniq_card=dest.order_uniq_card

        WHEN NOT MATCHED THEN 
            INSERT (order_uniq_card, order_date, ship_date, ship_mode)
            VALUES (src.order_uniq_card, src.order_date, src.ship_date, src.ship_mode);

    ------------------------------------------------
    -- sales
    MERGE INTO core.sales dest
    USING (
        SELECT DISTINCT co.id as order_id, cca.customer_id, cpe.id as product_id, ss.discount, ss.profit
        FROM stage.super_store ss
        INNER JOIN core.orders co ON co.order_uniq_card=ss.order_uniq_card AND
                                     co.order_date=ss.order_date AND 
                                     co.ship_date=ss.ship_date AND 
                                     co.ship_mode=ss.ship_mode
        INNER JOIN core.product_entities cpe ON cpe.product_uniq_card=ss.product_uniq_card AND
                                                cpe.product_name=ss.product_name
        INNER JOIN core.customers cc ON cc.customer_uniq_card=ss.customer_uniq_card
        INNER JOIN core.locations cl ON cl.country=ss.country AND cl.city=ss.city AND
                                        cl._state=ss._state AND cl.postal_code=ss.postal_code AND
                                        cl.region=ss.region
        INNER JOIN core.customer_accounts cca ON cca.customer_id=cc.id AND cca.location_id=cl.id
        WHERE cca.is_active = TRUE                           
    ) src
    ON src.order_id = dest.order_id AND src.product_id = dest.product_id

    WHEN MATCHED AND dest.active_customer_id IS DISTINCT FROM src.customer_id THEN
        UPDATE 
        SET active_customer_id = src.customer_id

    WHEN NOT MATCHED THEN
        INSERT (order_id, active_customer_id, product_id, discount, profit)
        VALUES (src.order_id, src.customer_id, src.product_id, src.discount, src.profit);

    
    TRUNCATE TABLE stage.super_store;
    DROP TABLE scd2;
    --*/
END;
$$;