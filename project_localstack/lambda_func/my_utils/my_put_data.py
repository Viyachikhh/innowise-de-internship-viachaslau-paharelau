import pandas as pd
import io
import json
import logging
from decimal import Decimal

from my_utils.my_interface import LocalstackBotoInterface
from my_utils.my_extract_data import chunk_grouped_data_extraction
from my_utils.my_calculate_metrics import calculate_average_metrics

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
    chunks = pd.read_csv(io.BytesIO(data), chunksize=20000, low_memory=False)

    # Чтение промежуточных метрик
    df_daily, df_monthly = chunk_grouped_data_extraction(chunks)

    # Расчёт метрик
    daily_info = calculate_average_metrics(df_daily, ['Period', 'DayNum'])
    monthly_info = calculate_average_metrics(df_monthly, ['Period'])

    # Вызов таблиц
    table_daily = interface.get_dynamo_resource.Table("DailyMetrics")
    table_monthly = interface.get_dynamo_resource.Table("MonthlyMetrics")

    # Помещаем данные
    with table_daily.batch_writer() as batch:
        for item in daily_info:
            batch.put_item(Item=item)

    with table_monthly.batch_writer() as batch:
        for item in monthly_info:
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

