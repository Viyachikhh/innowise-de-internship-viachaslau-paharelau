import pandas as pd

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable


with DAG('dataframe_split', schedule_interval=None, catchup=False) as dag:

    @task(task_id='big_df_splitting')
    def split(source_file: str, dest_path: str):
        df = pd.read_csv(source_file)
        df['departure'] = pd.to_datetime(df['departure'])
        for period, sample in df.groupby(df.departure.dt.month_name()):
            csv_name = '/' + str(period) + '.csv'
            sample.to_csv(dest_path + csv_name, index=False)

    source_folder = Variable.get("source_data_path")
    destination_folder = Variable.get("destination_data_path")

    source_file = source_folder + '/database.csv'

    split(source_file, destination_folder)