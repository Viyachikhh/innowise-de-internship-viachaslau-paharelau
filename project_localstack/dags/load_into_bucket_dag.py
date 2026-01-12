from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime
import boto3
import os

with DAG('communication_with_localstack', start_date=datetime(2026, 1, 1),schedule_interval='@daily', catchup=False) as dag:

    @task(task_id="appending_smaller_df")
    def append_into_bucket(csv_name: str):
        s3_client = boto3.client('s3',
                endpoint_url=os.environ.get("AWS_ENDPOINT"),
                aws_access_key_id=os.environ.get("AWS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS"),
                region_name=os.environ.get("AWS_REGION"))
        
        dest_inside_bucket = "months" + f'/{csv_name.split('/')[-1].split('.')[0]}' + '/data.csv'
        s3_client.upload_file(csv_name, "departure-info", dest_inside_bucket)

    calculate = SparkSubmitOperator(
        task_id='calculate_metrics',
        application='/opt/airflow/scripts/calculate_metrics.py', # Путь внутри контейнера Airflow
        conn_id='spark_default', # По умолчанию смотрит на spark://spark-master:7077 (нужно настроить или передать conf)
        packages="org.apache.hadoop:hadoop-aws:3.3.4", # Пакеты для S3
        verbose=True,
        application_args=["--month", "April"] 
    )

    month_example = Variable.get("destination_data_path") + '/April.csv'
    append_into_bucket(month_example) >> calculate