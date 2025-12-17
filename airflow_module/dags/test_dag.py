import os
import pprint
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import dag, DAG, Asset, task, Variable, task_group
from pendulum import datetime


def debug_env():
    print("--- НАЧАЛО ОТЛАДКИ ---")
    
    # 1. Ищем конкретную переменную (замените на вашу)
    target_var = "AIRFLOW_VAR_STORAGE" # <-- Вставьте ваше имя
    val = os.getenv(target_var)
    print(f"Поиск {target_var}: {val}")
    print(f"Variable = {Variable.get('storage')}")
    # 2. Если не нашли, ищем похожие (вдруг опечатка или регистр)
    print("Поиск похожих ключей:")
    for key in os.environ.keys():
        if "AIRFLOW_VAR" in key:
            print(f"  Found: {key}, {os.environ[key]}")
            
    print("--- КОНЕЦ ОТЛАДКИ ---")

with DAG(dag_id='debug_env_vars_task', start_date=datetime(2025, 12, 12), schedule='@once') as dag:
    t1 = PythonOperator(
        task_id='print_env',
        python_callable=debug_env
    )
    t1 