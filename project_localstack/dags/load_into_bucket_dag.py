import boto3
import os
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime
from pathlib import Path


with DAG('communication_with_localstack', start_date=datetime(2026, 1, 1),schedule_interval='@daily', catchup=False) as dag:

    @task(task_id="parse_dfs")
    def parse_csv():
        path = Variable.get("destination_data_path")
        dfs = list(Path(path).rglob("*.csv"))
        return [str(el) for el in dfs][6:7]
        
    @task(task_id="appending_smaller_df")
    def append_into_bucket(csv_name: str):
        hook = S3Hook(aws_conn_id='aws_localstack_default')
        
        month = csv_name.split('/')[-1].split('.')[0]
        dest_inside_bucket = "months" + f'/{month}' + '/data.csv'
        hook.load_file(filename=csv_name, key=dest_inside_bucket, bucket_name=os.environ.get("BUCKET_NAME"))
        return month
    
    @task(task_id="construct_spark_dynamic_args")
    def construct_args(name: str):
        return ['--month', name]


    files = parse_csv()
    appending_many = append_into_bucket.expand(csv_name=files)
    
    dynamic_spark_args = construct_args.expand(name=appending_many)

    
    calculate = SparkSubmitOperator.partial(
        task_id='calculate_metrics',
        application='/opt/airflow/scripts/calculate_metrics.py', 
        conn_id='spark_default',
        verbose=True).expand(application_args=dynamic_spark_args)
    
