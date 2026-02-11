from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.dynamodb import DynamoDBHook

import os
from datetime import datetime
import pandas as pd

from decimal import Decimal

with DAG(
    dag_id='dynamodb_to_csv_export',
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    @task
    def to_csv(table_name: str):

        # Получение данных
        db_hook = DynamoDBHook(aws_conn_id='aws_localstack_default')
        table = db_hook.get_conn().Table(table_name)
        items = table.scan().get('Items', [])
        if not items:
            return

        # Очистка Decimal для Pandas
        clean_decimal = lambda obj: float(obj) if isinstance(obj, Decimal) else obj
        cleaned_items = [{k: clean_decimal(v) for k, v in item.items()} for item in items]

        # Формируем DataFrame
        df = pd.DataFrame(cleaned_items)

        # Сохраняем локально
        full_path = os.path.join(Variable.get('exports_data_path'), f'{table_name}.csv')
        
        df.to_csv(full_path, index=False)

    tables = ['CountMetrics', 'DailyMetrics', 'MonthlyMetrics']
    to_csv.expand(table_name=tables)