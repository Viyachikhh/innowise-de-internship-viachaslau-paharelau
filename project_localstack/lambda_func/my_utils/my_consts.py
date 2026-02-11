
YEARS = [f'periods/{i}' for i in range(2014, 2022)]
MONTHS = [f'{i:02d}' for i in range(1, 13)]

PERIODS = set(f'{year}-{month}' for month in MONTHS for year in YEARS)

MONTH_NAMES = set(["January", 'February', 'March', 'April', 
               'May', 'June', 'July', 'August', 
               'September', 'October', 'November', 'December'])

MONTH_PREFIXES = set(f'periods/{month}' for month in MONTH_NAMES)


ATTRIBUTES = {"sum_duration": ('duration (sec.)', 'sum'),
                  "count_duration": ('duration (sec.)', 'count'),
                  "sum_distance":('distance (m)', 'sum'),
                  "count_distance":('distance (m)', 'count'),
                  "sum_speed":('avg_speed (km/h)', 'sum'),
                  "count_speed":('avg_speed (km/h)', 'count'),
                  "sum_temperature":('Air temperature (degC)', 'sum'),
                  "count_temperature":('Air temperature (degC)', 'count')}