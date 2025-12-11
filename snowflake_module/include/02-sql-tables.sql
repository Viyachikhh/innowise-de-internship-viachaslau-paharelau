USE DATABASE airline;

CREATE OR REPLACE TABLE RAW.FLIGHTS (
    id INT PRIMARY KEY AUTOINCREMENT,
    pass_id CHAR(6),
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    gender VARCHAR(6),
    age INT,
    nationality VARCHAR(100),
    airport_source VARCHAR(200),
    country_code CHAR(2),
    country_name VARCHAR(200),
    continent_code VARCHAR(3),
    continent_name VARCHAR(20),
    departure_date DATE,
    airport_dest VARCHAR(3),
    pilot_name VARCHAR(201),
    flight_status VARCHAR(15),
    ticket_type VARCHAR(15),
    passenger_status VARCHAR(15)
);

CREATE OR REPLACE STREAM RAW.stream_from_raw_to_stage ON TABLE RAW.FLIGHTS;

CREATE OR REPLACE TABLE STAGE.FLIGHTS LIKE RAW.FLIGHTS;

CREATE OR REPLACE STREAM STAGE.stream_from_stage_to_analytics ON TABLE STAGE.FLIGHTS;

CREATE OR REPLACE TABLE ANALYTICS.PASSANGERS (
    id CHAR(6) PRIMARY KEY,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    gender VARCHAR(6),
    age INT,
    nationality VARCHAR(100),
    UNIQUE (firstname, lastname)
    --CONSTRAINT check_age CHECK (age between 1 and 130),
    --CONSTRAINT check_gender CHECK (gender in ("Male", "Female")) 
);

CREATE OR REPLACE TABLE ANALYTICS.PILOTS (
    id INT PRIMARY KEY AUTOINCREMENT,
    fullname VARCHAR(201)
);

CREATE OR REPLACE TABLE ANALYTICS.COUNTRIES (
    code CHAR(2) PRIMARY KEY,
    name VARCHAR(200),
    UNIQUE (code)
    
);

CREATE OR REPLACE TABLE ANALYTICS.CONTINENTS (
    code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(20),
    UNIQUE (code)
);


CREATE OR REPLACE TABLE ANALYTICS.AIRPORT_SOURCE (
    id INT PRIMARY KEY AUTOINCREMENT, 
    airport_name VARCHAR(200),
    country_code CHAR(2),
    continent_code VARCHAR(3),
    FOREIGN KEY (country_code) REFERENCES ANALYTICS.COUNTRIES(code),
    FOREIGN KEY (continent_code) REFERENCES ANALYTICS.CONTINENTS(code)
);




CREATE OR REPLACE TABLE ANALYTICS.AIRPORT_DEST (
    id INT PRIMARY KEY AUTOINCREMENT, 
    airport_name CHAR(3)
);


CREATE OR REPLACE TABLE ANALYTICS.FACT_FLIGHTS (
    id INT PRIMARY KEY AUTOINCREMENT, 
    pass_id CHAR(6),
    departure_date DATE,
    airport_source_id INT, 
    airport_dest_id INT,
    pilot_id INT,
    flight_status VARCHAR(15),
    ticket_type VARCHAR(15),
    passenger_status VARCHAR(15),
    FOREIGN KEY (pass_id) REFERENCES ANALYTICS.PASSANGERS(id),
    FOREIGN KEY (airport_source_id) REFERENCES ANALYTICS.AIRPORT_SOURCE(id),
    FOREIGN KEY (airport_dest_id) REFERENCES ANALYTICS.AIRPORT_DEST(id),
    FOREIGN KEY (pilot_id) REFERENCES ANALYTICS.PILOTS(id)
);

CREATE OR REPLACE TABLE LOGGING.ID_LOG (
    id NUMBER IDENTITY(1,1) ORDER, 
    procedure_name VARCHAR(75),
    stage_source_name VARCHAR(15),
    stage_destination_name VARCHAR(15),
    table_name VARCHAR(15),
    affected_row_count INT
);