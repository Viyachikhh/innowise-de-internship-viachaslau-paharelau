import pandas as pd

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable


with DAG('dataframe_split', schedule_interval=None, catchup=False) as dag:

    @task(task_id='big_df_splitting')
    def split(source_file: str, dest_path: str):
        df = pd.read_csv(source_file)
        df['departure'] = pd.to_datetime(df['departure'])
        for month, sample in df.groupby(df.departure.dt.month):
            csv_name = str(month) + '.csv'
            print(dest_path + csv_name)
            sample.to_csv(dest_path + csv_name, index=False)

    main_path = Variable.get("data_path")

    source_file = main_path + '/orig/' + 'database.csv'
    dest_path = main_path + '/splitted/'

    split(source_file, main_path)