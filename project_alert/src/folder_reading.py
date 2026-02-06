from pathlib import Path


def check_filex_exists(source_path: str = '/logs/source', tracked_path: str = '/logs/tracked'):
    """
    Docstring for read_folder

    :param path: Description
    :type path: str
    """
    # Читаем директорию (обычно /logs/source/)
    folder_source_elements = list(Path(source_path).rglob("*.csv"))
    source_names = set(str(el).split('/')[-1] for el in folder_source_elements)
    # Читаем директорию, куда кинули предобработанные
    folder_tracked_elements = list(Path(tracked_path).rglob("*.csv"))
    tracked_names = set(str(el).split('/')[-1] for el in folder_tracked_elements)
    # Проверяем, есть ли новые файлы
    new_names = source_names - tracked_names

    return new_names if len(new_names) > 0 else False