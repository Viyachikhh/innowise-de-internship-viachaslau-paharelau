from airflow.sdk import task, DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeSqlApiOperator, SQLExecuteQueryOperator
from pendulum import datetime


default_args = {"snowflake_conn_id": "snowflake_conn", "conn_id": "snowflake_conn"}

with DAG(dag_id="lms_snowflake_task", start_date=datetime(2025, 11, 11), schedule="@daily", default_args=default_args) as dag:


    raw_to_stage = SQLExecuteQueryOperator(
        task_id='id_snowflake_from_raw_to_stage',
        sql="USE WAREHOUSE COMPUTE_WH;\ncall RAW.pr_data_from_raw_to_stage();"
    )

    stage_to_analytics = SQLExecuteQueryOperator(
        task_id='id_snowflake_from_stage_to_analytics',
        sql="USE WAREHOUSE COMPUTE_WH;\nUSE SCHEMA STAGE;\ncall airline.STAGE.pr_data_from_stage_to_analytics();"
        )

    raw_to_stage >> stage_to_analytics
    