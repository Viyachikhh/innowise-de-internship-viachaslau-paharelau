USE DATABASE airline;


CREATE OR REPLACE TABLE security.analytic_continent_access (
    allowed_continent_code VARCHAR(3),
    role_name VARCHAR(20)
);

-- Наполняем правилами
INSERT INTO security.analytic_continent_access (allowed_continent_code, role_name) VALUES 
('NAM', 'NAM_ANALYTIC'),
('EU', 'EU_ANALYTIC'),
('SAM', 'SAM_ANALYTIC'),
('AS', 'AS_ANALYTIC'),
('AF', 'AF_ANLYTIC'),
('OC', 'OC_ANALYTIC');

CREATE OR REPLACE ROW ACCESS POLICY security.continent_policy 
AS (continent_code VARCHAR) RETURNS BOOLEAN ->
  CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN')
  OR
  EXISTS (
      SELECT 1 
      FROM security.analytic_continent_access 
      WHERE role_name = CURRENT_ROLE() 
        AND allowed_continent_code = continent_code
  );

ALTER TABLE analytics.continents
ADD ROW ACCESS POLICY security.continent_policy ON (code); 

USE SCHEMA ANALYTICS;


USE ROLE ACCOUNTADMIN;

--тестировалось на первой тысячи записей, для eu_analytic выведет только 120
select count(*) from fact_flights inner join airport_source ais on airport_source_id = ais.id
                                  inner join continents c on  ais.continent_code = c.code; 
