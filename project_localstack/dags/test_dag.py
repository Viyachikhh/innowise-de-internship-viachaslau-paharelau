from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import os

# Настройки по умолчанию
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
}

def create_bucket_fn():
    """Создает бакет в LocalStack перед запуском Spark"""
    s3 = boto3.client(
        's3',
        endpoint_url=os.environ.get("AWS_ENDPOINT"),
        aws_access_key_id=os.environ.get("AWS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS"),
        region_name=os.environ.get("AWS_REGION")
    )
    print(os.environ.get("AWS_KEY_ID"))
    try:
        s3.create_bucket(Bucket='my-test-bucket')
        print("Bucket created")
    except Exception as e:
        print(f"Bucket might already exist: {e}")

with DAG('spark_localstack_demo', default_args=default_args, schedule_interval=None, catchup=False) as dag:

    # 1. Создание бакета в LocalStack
    create_bucket = PythonOperator(
        task_id='create_s3_bucket',
        python_callable=create_bucket_fn
    )

    # 2. Запуск PySpark джобы
    # Мы используем пакеты org.apache.hadoop:hadoop-aws для работы с S3
    submit_job = SparkSubmitOperator(
        task_id='submit_spark_job',
        application='/opt/airflow/scripts/job.py', # Путь внутри контейнера Airflow
        conn_id='spark_default', # По умолчанию смотрит на spark://spark-master:7077 (нужно настроить или передать conf)
        packages="org.apache.hadoop:hadoop-aws:3.3.4", # Пакеты для S3
        verbose=True
    )

    create_bucket >> submit_job