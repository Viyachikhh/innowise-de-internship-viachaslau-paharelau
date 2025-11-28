import pandas as pd

from airflow.sdk import dag, DAG, Asset, task, Variable, Connection, task_group, get_current_context
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.mongo.hooks.mongo import MongoHook

from pathlib import Path
from pendulum import datetime
from datetime import timedelta

import time


asset_df = Asset(uri="/home/viyachikhh/projects/innowise-internship/airflow_module/file_storage/preprocessed/data.csv", name='preprocessed_csv_path')

with DAG(dag_id='lms_dag_one', 
    schedule='@daily', 
    start_date=datetime(2025, 10, 10),
    tags=['lms', 'study'],
    description="First dag which check file existence and preprocessing with pandas"):
    
    @task.sensor(task_id='waiting_for_file', poke_interval=120, timeout=600, mode='reschedule')
    def check_file_exists():
        data_path = Path(Variable.get("raw_data_path_file", deserialize_json=True))
    
        if data_path.exists():
            condition_met = True
        else:
            condition_met = False

        return PokeReturnValue(is_done=condition_met, xcom_value=str(data_path))


    @task.branch(task_id='branching')
    def define_flow_path():
        if Path(Variable.get("raw_data_path_file", deserialize_json=True)).stat().st_size == 0:
            return 'bash_script'
        else:
            return 'preprocessing'


    @task.bash(task_id='bash_script')
    def bash_log():
        return "echo 'Folder is empty/file doesn\'t exist now.Wait for file\n'"
    

    @task_group(group_id='preprocessing')
    def preprocessing():
        
        @task(task_id='df_loading')
        def load_file(filename: str) -> pd.DataFrame:
            df = pd.read_csv(filename)
            return df[:50000]

        @task(task_id='df_replacing_nan', execution_timeout=timedelta(minutes=2))
        def replace_nan(df: pd.DataFrame) -> pd.DataFrame:
            df.fillna('-', inplace=True)
            return df

        @task(task_id='df_sorting')
        def sort(df: pd.DataFrame) -> pd.DataFrame:
            df.sort_values(by=['at'], inplace=True)
            return df

        @task(task_id='df_content_cleaning', outlets=[asset_df])
        def clean(df: pd.DataFrame):
            df['content'] = df['content'].str.replace(r'[^a-zA-Z0-9\.,:!?;\'\"-]+', ' ', regex=True).str.strip()
            return df

        @task(task_id='df_saving', outlets=[asset_df])
        def save(df: pd.DataFrame, new_path: str):
            print(new_path)
            df.to_csv(new_path, index=False)

        old_path = Variable.get("raw_data_path_file", deserialize_json=True)
        new_path = Variable.get("prep_data_path_file", deserialize_json=True)

        df = load_file(old_path)
        df_replaced = replace_nan(df)
        df_sorted = sort(df_replaced)
        df_cleaned = clean(df_sorted)
        save(df_cleaned, new_path)

    check_file_exists() >> define_flow_path() >> [bash_log(), preprocessing()]



with DAG(dag_id='lms_dag_two', 
    schedule=[asset_df], 
    start_date=datetime(2025, 10, 10),
    tags=['lms', 'study'],
    description="Second dag triggered by Asset from first dag"):


    @task(task_id='df_loading_preprocessed')
    def load_file() -> pd.DataFrame:
        path = Variable.get("prep_data_path_file", deserialize_json=True)
        df = pd.read_csv(path)
        return df
    
    @task(task_id='df_inserting_to_database')
    def load_to_database(df: pd.DataFrame):

        db_name = Variable.get("db_study_name", deserialize_json=True)

        hook = MongoHook(mongo_conn_id="mongo_default")
        db = hook.get_conn()[db_name]
        collection = db[Variable.get("db_mongo_collection", deserialize_json=True)]

        df.reset_index(inplace=True)
        data_dict = df.to_dict("records")
        collection.insert_many(data_dict)


    df = load_file()
    load_to_database(df)
    # Path(path).unlink(missing_ok=True)