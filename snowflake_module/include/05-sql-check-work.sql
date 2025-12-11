insert into airline.raw.flights 
select flight_id, af.pass_id, first_name, 
            last_name, af.gender, af.age,
            af.nationality, af.airport_source, af.country_code,
            af.country_name, af.continent_code, af.continent_name,
            af.departure_date, airport_destination, pilot_fullname,
            af.flight_status, af.ticket_type, pass_status
from airline.public.flights af where flight_id between 1 and 1000;
call airline.RAW.pr_data_from_raw_to_stage();
call airline.STAGE.pr_data_from_stage_to_analytics();
--select * from airline.RAW.stream_from_raw_to_stage;
--select * from airline.STAGE.stream_from_stage_to_analytics;

--select * from airline.LOGGING.ID_LOG;
--select * from airline.analytics.fact_flights;
--select * from airline.analytics.airport_dest;
--select distinct continent_code from airline.analytics.airport_source;
--select * from airline.public.flights where airport_destination = '0';