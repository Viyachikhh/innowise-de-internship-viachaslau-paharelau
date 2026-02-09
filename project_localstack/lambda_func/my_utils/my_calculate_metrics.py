import pandas as pd
import json

from typing import Iterable
from decimal import Decimal

def calculate_average_metrics(df: pd.DataFrame, predicate_columns: Iterable[str]) -> dict:
    """
    Расчёт метрик среднего значения для датафреймов
    В данном случае duration, distance, temperature, speed
    
    :param df: Датафрейм (для корректного расчёта должны быть колонки sum_attr и count_attr)
    :type df: pd.DataFrame (пока только для pandas датафрейма)
    :param predicate_columns: Колонки данных, по которым производилась группировка
    :type predicate_columns: Iterable[str]
    :return: словарь записей, которые пойдут в DynamoDB
    """
    df['AvgDuration'] = df['sum_duration'] / df['count_duration']
    df['AvgDistance'] = df['sum_distance'] / df['count_distance']
    df['AvgSpeed'] = df['sum_speed'] / df['count_speed']
    df['AvgTemperature'] = df['sum_temperature'] / df['count_temperature']

    df = df[['AvgDuration', 'AvgDistance', 'AvgSpeed', 'AvgTemperature']]
    df.index.names = predicate_columns
    records = json.loads(df.reset_index().to_json(orient='records', default_handler=str), parse_float=Decimal)
    return records