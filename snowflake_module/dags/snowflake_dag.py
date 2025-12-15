from airflow import DAG
from airflow.decorators import task
from airflow.providers.snowflake.operators.snowflake import SnowflakeSqlApiOperator, SQLExecuteQueryOperator
from pendulum import datetime
from datetime import timedelta


with DAG(dag_id="lms_snowflake_task", 
        start_date=datetime(2025, 11, 11), 
        schedule="@daily", 
        default_args = {"snowflake_conn_id": "snowflake_default", 
        "conn_id": "snowflake_default"},
        catchup=False) as dag:

    @task(task_id='test')
    def print_test():
        print("snowflake_deafult")

    raw_to_stage = SQLExecuteQueryOperator(
        task_id='id_snowflake_from_raw_to_stage',
        sql="USE WAREHOUSE COMPUTE_WH;\ncall RAW.pr_data_from_raw_to_stage();"
    )

    stage_to_analytics = SQLExecuteQueryOperator(
        task_id='id_snowflake_from_stage_to_analytics',
        sql="USE WAREHOUSE COMPUTE_WH;\nUSE SCHEMA STAGE;\ncall airline.STAGE.pr_data_from_stage_to_analytics();"
        )

    print_test() >> raw_to_stage >> stage_to_analytics
    