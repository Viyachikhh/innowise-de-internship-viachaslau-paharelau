import shutil
from pathlib import Path
from typing import Iterable


def move_data(csv_names: Iterable[str], source_path: str, tracked_path: str) -> None:
    """
    Перемещаем данные из source в tracked
    
    :param csv_names: csv, над котороыми проводилась проверка
    :type csv_names: Iterable[str]
    :param source_path: Description
    :type source_path: str
    :param destination_path: Description
    :type destination_path: str
    """
    for file in csv_names:
        source = f'{source_path}/{file}'
        target = f'{tracked_path}/{file}' 
        
        shutil.move(source, target)