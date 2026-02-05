import pandas as pd
import io
import json
import logging
from decimal import Decimal

from my_utils.my_interface import LocalstackBotoInterface

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def data_metric_logic(interface: LocalstackBotoInterface, bucket:str, key:str):
    """
    Помещает файлы из S3 бакета в DynamoDB (Ежедневные и ежегодные метрики)
    
    :param interface: Кастомный объект, который хранит в себе модули boto3
    :type interface: LocalstackBotoInterface
    :param bucket: Бакет, откуда берём информацию
    :type bucket: str
    :param key: Ключ к файлу, из которого мы собираем информацию
    :type key: str
    """
    obj = interface.get_s3_client.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read()
    chunks = pd.read_csv(io.BytesIO(data), chunksize=10000, low_memory=False)

    for chunk in chunks:
        chunk['departure'] = pd.to_datetime(chunk['departure'])

        period = chunk['departure'].dt.to_period('M').unique().tolist()[0]

        chunk_metrics = chunk.groupby(chunk.departure.dt.day).agg(sum_duration=('duration (sec.)', 'sum'),
                                                                count_duration=('duration (sec.)', 'count'),
                                                                sum_distance=('distance (m)', 'sum'),
                                                                count_distance=('distance (m)', 'count'),
                                                                sum_speed=('avg_speed (km/h)', 'sum'),
                                                                count_speed=('avg_speed (km/h)', 'count'),
                                                                sum_temperature=('Air temperature (degC)', 'sum'),
                                                                count_temperature=('Air temperature (degC)', 'count'))
        if 'full_df' not in locals():
            full_df = chunk_metrics
        else:
            full_df = full_df.add(chunk_metrics, fill_value=0)

    # Расчёт полных метрик для DailyMetrics
    full_df['AvgDuration'] = full_df['sum_duration'] / full_df['count_duration']
    full_df['AvgDistance'] = full_df['sum_distance'] / full_df['count_distance']
    full_df['AvgSpeed'] = full_df['sum_speed'] / full_df['count_speed']
    full_df['AvgTemperature'] = full_df['sum_temperature'] / full_df['count_temperature']

    # Выделение отдельного датафрейма
    daily_df = full_df[['AvgDuration', 'AvgDistance', 'AvgSpeed', 'AvgTemperature']]
    daily_df['Period'] = str(period)
    daily_df.index.names = ['DayNum']

    # Для корректной конвертации данных
    convert = lambda x: Decimal(str(x))
    # Данные в json
    daily_info = json.loads(daily_df.reset_index().to_json(orient='records'), parse_float=Decimal)
    month_info = [{'Period': str(period), 
                'AvgDuration': convert(full_df['sum_duration'].sum() / full_df['count_duration'].sum()), 
                'AvgDistance': convert(full_df['sum_distance'].sum() / full_df['count_distance'].sum()), 
                'AvgSpeed': convert(full_df['sum_speed'].sum() / full_df['count_speed'].sum()), 
                'AvgTemperature': convert(full_df['sum_temperature'].sum() / full_df['count_temperature'].sum())}]
    
    # Вызов таблиц
    table_daily = interface.get_dynamo_resource.Table("DailyMetrics")
    table_monthly = interface.get_dynamo_resource.Table("MonthlyMetrics")

    # Помещаем данные
    with table_daily.batch_writer() as batch:
        for item in daily_info:
            batch.put_item(Item=item)

    with table_monthly.batch_writer() as batch:
        for item in month_info:
            batch.put_item(Item=item)
    
    

def spark_metric_logic(interface: LocalstackBotoInterface, bucket:str, key:str):
    """
    Помещаем файл из S3 бакета в DynamoDB (Метрики о количестве прилётов и полётов)
    
    :param interface: Кастомный объект, который хранит в себе модули boto3
    :type interface: LocalstackBotoInterface
    :param bucket: Бакет, откуда берём информацию
    :type bucket: str
    :param key: Ключ к файлу, из которого мы собираем информацию
    :type key: str
    """
    # Чтение датафрема 
    obj = interface.get_s3_client.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read()
    df = pd.read_csv(io.BytesIO(data), low_memory=False)

    # Преобразование в list[dict]
    items = json.loads(df.reset_index().to_json(orient='records'), parse_float=Decimal)
    items = [{k: v for k, v in item.items() if k != 'index'} for item in items]

    # Вызов таблицы
    table_counts = interface.get_dynamo_resource.Table("CountMetrics")
    
    # Помещаем данные
    with table_counts.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

