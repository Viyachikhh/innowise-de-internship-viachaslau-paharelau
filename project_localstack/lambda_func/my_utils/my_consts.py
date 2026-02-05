
YEARS = [f'periods/{i}' for i in range(2014, 2022)]
MONTHS = [f'{i:02d}' for i in range(1, 13)]

PERIODS = set(f'{year}-{month}' for month in MONTHS for year in YEARS)
