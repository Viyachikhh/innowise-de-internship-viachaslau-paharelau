USE DATABASE airline;
USE WAREHOUSE COMPUTE_WH;

CREATE OR REPLACE PROCEDURE airline.RAW.pr_data_from_raw_to_stage()
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE 
    rows_inserted INT;
    error_message VARCHAR;
BEGIN
    BEGIN TRANSACTION;
        MERGE INTO airline.STAGE.FLIGHTS tt
        USING (SELECT id, pass_id, firstname, lastname, gender, age, 
        nationality, airport_source, country_code, country_name, 
        continent_code, continent_name, departure_date, airport_dest,
        pilot_name, flight_status, ticket_type, passenger_status, 
        FROM airline.RAW.stream_from_raw_to_stage WHERE METADATA$ACTION = 'INSERT') ss
        ON tt.id = ss.id and tt.departure_date = ss.departure_date
        WHEN NOT MATCHED 
        THEN INSERT VALUES 
            (ss.id, ss.pass_id, 
             ss.firstname, ss.lastname, 
             ss.gender, ss.age, 
             ss.nationality, ss.airport_source, 
             ss.country_code, ss.country_name, 
             ss.continent_code, ss.continent_name, 
             ss.departure_date, ss.airport_dest,
             ss.pilot_name, ss.flight_status, 
             ss.ticket_type, ss.passenger_status);
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_row_to_stage', 'RAW', 'STAGE', 'flights', :rows_inserted);
        TRUNCATE TABLE airline.RAW.flights;
        COMMIT;
        RETURN 'Inserted ' ||  :rows_inserted || ' rows.';
    EXCEPTION
        WHEN OTHER THEN
            ROLLBACK;
        error_message := 'Error: ' || SQLCODE || ' - ' || SQLERRM;
        RETURN 'Error: transaction was rejected. ' || :error_message;
END;
$$;


CREATE OR REPLACE PROCEDURE airline.STAGE.pr_data_from_stage_to_analytics()
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE 
    rows_inserted INT;
    error_message VARCHAR;
    error_query_line INT DEFAULT 0;
BEGIN
    BEGIN TRANSACTION;
        
        --passangers
        MERGE INTO airline.ANALYTICS.PASSANGERS ps
            USING (SELECT DISTINCT 
                    pass_id, firstname, lastname, 
                    gender, age, nationality 
                    FROM airline.STAGE.stream_from_stage_to_analytics WHERE METADATA$ACTION = 'INSERT') sv
            ON ps.id = sv.pass_id
            WHEN NOT MATCHED THEN 
            INSERT 
            VALUES (sv.pass_id, sv.firstname, sv.lastname, sv.gender, sv.age, sv.nationality);
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'passangers', :rows_inserted);

        error_query_line := 1;

        

        --countries
        MERGE INTO airline.ANALYTICS.COUNTRIES ac
            USING (SELECT DISTINCT country_code, country_name
                    FROM airline.STAGE.stream_from_stage_to_analytics 
                    WHERE METADATA$ACTION = 'INSERT') asvc
            ON ac.code = asvc.country_code
            WHEN NOT MATCHED THEN 
            INSERT (code, name)
            VALUES (asvc.country_code, asvc.country_name);
            
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'countries', :rows_inserted);


        error_query_line := 2;



        --continents
        MERGE INTO airline.ANALYTICS.CONTINENTS acc
            USING (SELECT DISTINCT continent_code, continent_name
                    FROM airline.STAGE.stream_from_stage_to_analytics 
                    WHERE METADATA$ACTION = 'INSERT') asvc
            ON acc.code = asvc.continent_code
            WHEN NOT MATCHED THEN 
            INSERT (code, name)
            VALUES (asvc.continent_code, asvc.continent_name);
            
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'continents', :rows_inserted);
        
        error_query_line := 3;
        
        
        --airport_source
        MERGE INTO airline.ANALYTICS.AIRPORT_SOURCE aas
            USING (SELECT DISTINCT airport_source, ac.code as country_code, acc.code as continent_code
                    FROM airline.STAGE.stream_from_stage_to_analytics ssv
                    LEFT JOIN airline.ANALYTICS.COUNTRIES ac ON ssv.country_name = ac.name
                    LEFT JOIN airline.ANALYTICS.CONTINENTS acc ON ssv.continent_name = acc.name
                    WHERE METADATA$ACTION = 'INSERT') asvc
            ON aas.airport_name = asvc.airport_source 
            
            WHEN NOT MATCHED THEN 
            INSERT (airport_name, country_code, continent_code)
            VALUES (asvc.airport_source, asvc.country_code, asvc.continent_code);
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'airport_source', :rows_inserted);


         error_query_line := 4;





        --airport_destination
        MERGE INTO airline.ANALYTICS.AIRPORT_DEST aad
            USING (SELECT DISTINCT airport_dest
                   FROM airline.STAGE.stream_from_stage_to_analytics WHERE METADATA$ACTION = 'INSERT') adv
            ON aad.airport_name = adv.airport_dest
            
            WHEN NOT MATCHED THEN 
            INSERT (airport_name)
            VALUES (adv.airport_dest);
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'airport_dest', :rows_inserted);



         error_query_line := 5;




        --pilots
        MERGE INTO airline.ANALYTICS.PILOTS ap
            USING (SELECT DISTINCT pilot_name
                   FROM airline.STAGE.stream_from_stage_to_analytics WHERE METADATA$ACTION = 'INSERT') pv
            ON ap.fullname = pv.pilot_name
            
            WHEN NOT MATCHED THEN 
            INSERT (fullname)
            VALUES (pv.pilot_name);
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'pilots', :rows_inserted);


         error_query_line := 6;



        --flights
        INSERT INTO airline.ANALYTICS.FACT_FLIGHTS
        SELECT fsv.id, aps.id, fsv.departure_date, 
            aas.id, aad.id, ap.id, fsv.flight_status, 
            fsv.ticket_type, fsv.passenger_status 
            FROM airline.STAGE.stream_from_stage_to_analytics fsv 
            LEFT JOIN airline.ANALYTICS.PASSANGERS aps ON fsv.pass_id = aps.id
            LEFT JOIN airline.ANALYTICS.AIRPORT_SOURCE aas ON fsv.airport_source = aas.airport_name
            LEFT JOIN airline.ANALYTICS.AIRPORT_DEST aad ON fsv.airport_dest = aad.airport_name
            LEFT JOIN airline.ANALYTICS.PILOTS ap ON fsv.pilot_name = ap.fullname WHERE METADATA$ACTION = 'INSERT';
        rows_inserted := SQLROWCOUNT;
        
        INSERT INTO airline.LOGGING.ID_LOG 
        (procedure_name, stage_source_name, stage_destination_name, table_name, affected_row_count) 
        VALUES ('pr_data_from_stage_to_analytics', 'STAGE', 'ANALYTICS', 'flights', :rows_inserted);

         error_query_line := 7;
        TRUNCATE TABLE airline.STAGE.flights;

        
    COMMIT;
    RETURN 'Inserted ' || :rows_inserted || ' rows. Check ID_LOG table.';
    
    EXCEPTION
        WHEN OTHER THEN
            ROLLBACK;
        error_message := 'Error: ' || SQLCODE || ' - ' || SQLERRM || ' - ' || 'LINE: ' || :error_query_line;
        RETURN 'Error: transaction was rejected. ' || :error_message;
END;
$$;