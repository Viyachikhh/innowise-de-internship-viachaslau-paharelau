import os
import pandas as pd
import time

from airflow.sdk import dag, DAG, Asset, task, Variable, task_group
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.mongo.hooks.mongo import MongoHook

from pathlib import Path
from pendulum import datetime
from datetime import timedelta


asset_df = Asset(uri=os.getenv('AIRFLOW_VAR_STORAGE') + '/preprocessed/data.csv', 
                name='preprocessed_csv')

with DAG(dag_id='lms_dag_one', 
    schedule='@daily', 
    start_date=datetime(2025, 10, 10),
    tags=['lms', 'study'],
    description="First dag which check file existence and preprocessing with pandas",
    dagrun_timeout=timedelta(minutes=3)):
    
    @task.sensor(task_id='waiting_for_file', poke_interval=120, timeout=600, mode='reschedule')
    def check_file_exists(ti):
        file_storage_path = Variable.get('STORAGE')
        raw_path = file_storage_path + '/raw'
        csv_list = list(Path(raw_path).glob("*.csv"))
    
        if len(csv_list) > 0:
            xcom_value = str(csv_list[0])
            condition_met = True
            ti.xcom_push(key='file_path', value=xcom_value)
        else:
            xcom_value = None
            condition_met = False

        return PokeReturnValue(is_done=condition_met, xcom_value=xcom_value)


    @task.branch(task_id='branching')
    def define_flow_path(ti):
        csv_name = ti.xcom_pull(key="file_path", task_ids="waiting_for_file")
        if pd.read_csv(csv_name).empty:
            return 'bash_script'
        else:
            return 'preprocessing'


    @task.bash(task_id='bash_script')
    def bash_log():
        return "echo 'Folder is empty/file doesn\'t exist now.Wait for file\n'"
    

    @task_group(group_id='preprocessing')
    def preprocessing():

        @task(task_id='df_replacing_nan')
        def replace_nan(filename: str) -> str:
            df = pd.read_csv(filename)
            df.fillna('-', inplace=True)
            df.to_csv(filename, index=False)
            return filename

        @task(task_id='df_sorting')
        def sort(filename: str) -> str:
            df = pd.read_csv(filename)
            df.sort_values(by=['at'], inplace=True)
            df.to_csv(filename, index=False)
            return filename

        @task(task_id='df_content_cleaning')
        def clean(filename: str):
            df = pd.read_csv(filename)
            df['content'] = df['content'].str.replace(r'[^a-zA-Z0-9\.,:!?;\'\"-]+', ' ', regex=True).str.strip()
            df.to_csv(filename, index=False)
            return filename

        @task(task_id='df_saving', outlets=[asset_df])
        def save_new_path(old_path: str, new_path: str):
            df = pd.read_csv(old_path)
            df.to_csv(new_path, index=False)

        file_storage_path = Variable.get('storage')
        raw_storage_path = file_storage_path + '/raw'
        new_storage_path = file_storage_path + '/preprocessed'
        csv_name = list(Path(raw_storage_path).glob("*.csv"))[0]

        raw_path = str(csv_name)
        new_path = new_storage_path + '/data.csv'

        raw_path = replace_nan(raw_path)
        raw_path = sort(raw_path)
        raw_path = clean(raw_path)
        save_new_path(raw_path, new_path)

    check_file_exists() >> define_flow_path() >> [bash_log(), preprocessing()]



with DAG(dag_id='lms_dag_two', 
    schedule=[asset_df], 
    start_date=datetime(2025, 10, 10),
    tags=['lms', 'study'],
    description="Second dag triggered by Asset from first dag",
    dagrun_timeout=timedelta(minutes=2)):

    @task(task_id='df_inserting_to_database')
    def load_to_database(filename: str):
        
        df = pd.read_csv(filename)
        
        db_name = Variable.get("db_name")

        hook = MongoHook(mongo_conn_id="mongo_conn")
        
        db = hook.get_conn()[db_name]
      
        collection = db[Variable.get("db_collection")]
       
        df.reset_index(inplace=True)
        data_dict = df.to_dict("records")
        
        collection.insert_many(data_dict)
   


    filepath = Variable.get('storage') + '/preprocessed' + '/data.csv'
    load_to_database(filepath)
    # Path(path).unlink(missing_ok=True)