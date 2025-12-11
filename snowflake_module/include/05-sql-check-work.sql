/*insert into airline.raw.flights 
select flight_id, af.pass_id, first_name, 
            last_name, af.gender, af.age,
            af.nationality, af.airport_source, af.country_code,
            af.country_name, af.continent_code, af.continent_name,
            af.departure_date, airport_destination, pilot_fullname,
            af.flight_status, af.ticket_type, pass_status
from airline.public.flights af where flight_id between 1 and 1000;
call airline.RAW.pr_data_from_raw_to_stage();
call airline.STAGE.pr_data_from_stage_to_analytics();
select * from airline.LOGGING.ID_LOG;
select * from airline.RAW.stream_from_raw_to_stage;
select * from airline.STAGE.stream_from_stage_to_analytics;

select * from airline.LOGGING.ID_LOG;
select * from airline.analytics.fact_flights;
select * from airline.analytics.airport_dest;
select distinct continent_code from airline.analytics.airport_source;
select * from airline.public.flights where airport_destination = '0';*/


--DDL
--восстановить удалённую таблицу через drop
UNDROP TABLE airline.analytics.airport_source;


--создать таблицу, на основе предыдущей, которая существовала 3 дня назад
CREATE TABLE airline.analytics.airport_source_prev_state CLONE airline.analytics.airport_source 
AT(OFFSET => -60*60*24*3);

--DML
--обновить записи таблицы, на основе предыдущей, которые существовали 7 дней назад и называются '0'
UPDATE airline.analytics.airport_dest airport
SET airport_name = 'Unknown'
FROM airport at(offset => -60 * 60 * 24 * 7)
WHERE airport_name = '0';


--обновить записи таблицы, на основе предыдущей, которые существовали 7 дней назад и называются '0'
INSERT INTO passangers
SELECT * 
FROM passangers AT(OFFSET => -60*60*24*3) -- Look at table state 300 seconds (5 mins) ago
WHERE nationality = 'Palestine Republic';