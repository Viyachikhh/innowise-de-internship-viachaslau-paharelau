import json
from pathlib import Path
from typing import Iterable

from src.df_preparation import reading, preparation
from src.folder_reading import check_filex_exists
from src.rules import BaseErrorCheck, BaseBundleErrorCheck
from src.log_aggregator import LogAggregator
from src.moving_data import move_data


def tracking(csv_names: Iterable[str], source_path: str ='/logs/source', tracked_path: str ='/logs/tracked'):

    # Получение csv
    dfs = [preparation(reading(f'{source_path}/{name}')) for name in csv_names]
    dicts = dict(zip(csv_names, dfs))
    # Объявление агрегатора ошибок
    aggregator = LogAggregator(BaseErrorCheck, BaseBundleErrorCheck)
    # Чтение данных
    error_list = aggregator.extract_fields(**dicts)
    # Перемещение проверенных csv
    move_data(csv_names, source_path, tracked_path)
    # Сохраняем в json
    with open(f"/logs/error_list/example.json", "a+") as ouptut:
        json.dump(error_list, ouptut, indent=4)
    

if __name__ == "__main__":
    files = check_filex_exists()
    if not files:
        print('THERE AREN\'T ANY NEW FILES')
    else:
        tracking(files)
