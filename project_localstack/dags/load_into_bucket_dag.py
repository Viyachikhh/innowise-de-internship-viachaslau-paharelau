import boto3
import os
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.apache.livy.operators.livy import LivyOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime
from pathlib import Path


with DAG('communication_with_localstack', start_date=datetime(2026, 1, 1),schedule_interval=None, catchup=False) as dag:

    @task(task_id="parse_dfs")
    def parse_csv():
        """
        Чтение данных из папки с csv по месяцам
        """
        path = Variable.get("destination_data_path")
        dfs = list(Path(path).rglob("*.csv"))
        return [str(el) for el in dfs]
        
    @task(task_id="appending_smaller_df")
    def append_into_bucket(csv_name: str):
        """
        Помещаем csv в S3 бакет
        
        :param csv_name: Имя csv
        :type csv_name: str
        """
        hook = S3Hook(aws_conn_id='aws_localstack_default')
        
        period = csv_name.split('/')[-1].split('.')[0]
        dest_inside_bucket = "periods" + f'/{period}' + '/data.csv'
        hook.load_file(filename=csv_name, key=dest_inside_bucket, bucket_name=os.environ.get("BUCKET_NAME"))
        return period
    
    @task(task_id="construct_spark_dynamic_args")
    def construct_args(name: str):
        """
        Строим аргументы для downstream-оператора,
        Для реализации DynamicTaskMapping
        
        :param name: Имя csv файла
        :type name: str
        """
        return ['--period', name]

    files = parse_csv()
    appending_many = append_into_bucket.expand(csv_name=files)
    dynamic_spark_args = construct_args.expand(name=appending_many)
    # Собственно сам оператор
    submit_spark_app = LivyOperator.partial(
        task_id='submit_spark_app',
        livy_conn_id='livy_default',
        file='local:///opt/livy/scripts/calculate_metrics.py',
        executor_cores=1,
        num_executors=4, 
        polling_interval=10,
        conf={
            "spark.hadoop.fs.s3a.endpoint": os.environ.get("AWS_ENDPOINT"), 
            "spark.hadoop.fs.s3a.access.key": os.environ.get("AWS_KEY_ID"),           
            "spark.hadoop.fs.s3a.secret.key": os.environ.get("AWS_SECRET_ACCESS"),        
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "spark.hadoop.fs.s3a.fast.upload": "true"
        }
    ).expand(args=dynamic_spark_args)