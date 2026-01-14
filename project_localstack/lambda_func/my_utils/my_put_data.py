import pandas as pd
import io
import json
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def data_metric_logic(interface, bucket, key):
    """
    Предобработка информации из DAG Airflow
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
    

    table_daily = interface.get_dynamo_resource.Table("DailyMetrics")
    table_monthly = interface.get_dynamo_resource.Table("MonthlyMetrics")

    # Помещаем данные
    with table_daily.batch_writer() as batch:
        for item in daily_items:
            batch.put_item(Item=item)

    with table_monthly.batch_writer() as batch:
        for item in monthly_item:
            batch.put_item(Item=item)
    
    

def spark_metric_logic(interface, bucket, key):
    """
    Предобработка информации из Spark, а затем из DAG
    """
    obj = interface.get_s3_client.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read()
    df = pd.read_csv(io.BytesIO(data), low_memory=False)

    items = json.loads(df.reset_index().to_json(orient='records'), parse_float=Decimal)
    table_counts = interface.get_dynamo_resource.Table("CountMetrics")
    
    with table_counts.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def dynamodb_append(interface, bucket, key):
    logger.info("A" * 150 + '\n\n' + f'{key}')
    spark_metric_logic(interface, bucket, key)

    key_prefix = key.split('/')[:2]
    key_data = '/'.join(key_prefix) + '/data.csv'
    logger.info("A" * 150 + '\n\n' + f'{key_data}')
    data_metric_logic(interface, bucket, key_data)



    