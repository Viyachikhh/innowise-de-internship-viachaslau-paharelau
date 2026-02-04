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
    df = pd.read_csv(io.BytesIO(data), low_memory=False)

    df['departure'] = pd.to_datetime(df['departure'])

    # Расчёт ежедневных метрик
    df_daily_metrics = df.groupby(df.departure.dt.day).agg({"distance (m)":"mean", 
                                "duration (sec.)":"mean", 
                                "avg_speed (km/h)":"mean", 
                                "Air temperature (degC)":"mean"}).reset_index().rename(columns={"distance (m)":"AvgDistance", 
                                                                                "duration (sec.)":"AvgDuration", 
                                                                                "avg_speed (km/h)":"AvgSpeed", 
                                                                                "Air temperature (degC)":"AvgTemperature",
                                                                                "departure": "DayNum"})
    
    df_daily_metrics['Month'] = df.departure.dt.month_name().tolist()[0]
    df_daily_metrics = df_daily_metrics[['Month', 'DayNum', 'AvgDistance', 'AvgDuration', 'AvgSpeed', 'AvgTemperature']]
    
    daily_items = json.loads(df_daily_metrics.reset_index().to_json(orient='records'), parse_float=Decimal)
    daily_items = [{k: v for k, v in item.items() if k != 'index'} for item in daily_items]
    
    # Расчёт ежемесячных (будет одна строка, т.к. у нас изначально идёт группировка по месяцам)
    df_monthly_metrics = df.groupby(df.departure.dt.month_name()).agg({"distance (m)":"mean", 
                                "duration (sec.)":"mean", 
                                "avg_speed (km/h)":"mean", 
                                "Air temperature (degC)":"mean"}).reset_index().rename(columns={"distance (m)":"AvgDistance", 
                                                                                "duration (sec.)":"AvgDuration", 
                                                                                "avg_speed (km/h)":"AvgSpeed", 
                                                                                "Air temperature (degC)":"AvgTemperature",
                                                                                "departure": "Month"})
    monthly_item = json.loads(df_monthly_metrics.reset_index().to_json(orient='records'), parse_float=Decimal)
    monthly_item[0]['index'] = df.departure.dt.month.tolist()[0]
    
    # Вызов таблиц
    table_daily = interface.get_dynamo_resource.Table("DailyMetrics")
    table_monthly = interface.get_dynamo_resource.Table("MonthlyMetrics")

    # Помещаем данные
    with table_daily.batch_writer() as batch:
        for item in daily_items:
            batch.put_item(Item=item)

    with table_monthly.batch_writer() as batch:
        for item in monthly_item:
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

