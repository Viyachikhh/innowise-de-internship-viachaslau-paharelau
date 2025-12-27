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
            SELECT DISTINCT cpc.product_uniq_card, ss.product_name 
            FROM stage.super_store ss
            INNER JOIN core.product_categories cpc ON ss.product_uniq_card=cpc.product_uniq_card
        ) src
        ON src.product_uniq_card=dest.product_uniq_card AND src.product_name=dest.product_name

        WHEN NOT MATCHED THEN 
            INSERT (product_uniq_card, product_name)
            VALUES (src.product_uniq_card, src.product_name);
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
    MERGE INTO core.order_statuses dest
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
    MERGE INTO core.sale_info dest
    USING (
        SELECT DISTINCT cos.id as order_id, cca.customer_id, cpe.id as product_id, ss.quantity, ss.discount, ss.profit, ss.sales
        FROM stage.super_store ss
        INNER JOIN core.order_statuses cos ON cos.order_uniq_card=ss.order_uniq_card AND
                                     cos.order_date=ss.order_date AND 
                                     cos.ship_date=ss.ship_date AND 
                                     cos.ship_mode=ss.ship_mode
        INNER JOIN core.product_entities cpe ON cpe.product_uniq_card=ss.product_uniq_card AND
                                                cpe.product_name=ss.product_name
        INNER JOIN core.customers cc ON cc.customer_uniq_card=ss.customer_uniq_card
        INNER JOIN core.locations cl ON cl.country=ss.country AND cl.city=ss.city AND
                                        cl._state=ss._state AND cl.postal_code=ss.postal_code AND
                                        cl.region=ss.region
        INNER JOIN core.customer_accounts cca ON cca.customer_id=cc.id AND cca.location_id=cl.id
        --WHERE cca.is_active = TRUE                           
    ) src
    ON src.order_id = dest.order_id AND src.product_id = dest.product_id

    WHEN MATCHED AND dest.active_customer_id IS DISTINCT FROM src.customer_id THEN
        UPDATE 
        SET active_customer_id = src.customer_id

    WHEN NOT MATCHED THEN
        INSERT (order_id, active_customer_id, product_id, quantity, discount, profit, sales)
        VALUES (src.order_id, src.customer_id, src.product_id, src.quantity, src.discount, src.profit, src.sales);

    
    TRUNCATE TABLE stage.super_store;
    DROP TABLE scd2;
    --*/
END;
$$;


CREATE OR REPLACE PROCEDURE core.update_mart()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE mart.analytic_sale_info;
    INSERT INTO mart.analytic_sale_info (
        order_date, ship_date, ship_mode, customer_name, segment,
        country, city, _state, postal_code, region, category, sub_category, 
        product_name, sales, quantity, discount, profit
    )
    SELECT DISTINCT
            cos.order_date, 
            cos.ship_date, 
            cos.ship_mode, 
            cc.customer_name, 
            cc.segment,
            cl.country, 
            cl.city,
            cl._state, 
            cl.postal_code, 
            cl.region, 
            cpc.category, 
            cpc.sub_category, 
            cpe.product_name, 
            csi.sales, 
            csi.quantity, 
            csi.discount, 
            csi.profit
            FROM core.sale_info csi
            INNER JOIN core.order_statuses cos ON csi.order_id=cos.id
            INNER JOIN core.customer_accounts cca ON csi.active_customer_id=cca.id
            INNER JOIN core.product_entities cpe ON csi.product_id=cpe.id
            INNER JOIN core.customers cc ON cca.customer_id=cc.id
            INNER JOIN core.locations cl ON cca.location_id=cl.id
            INNER JOIN core.product_categories cpc ON cpe.product_uniq_card=cpc.product_uniq_card;
END;
$$