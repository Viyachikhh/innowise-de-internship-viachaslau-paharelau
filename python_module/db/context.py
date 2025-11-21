import psycopg
import yaml


class DatabaseContext:
    """
    Менеджер контекста для работы с базой данных в PostgreSQL
    """

    def __init__(self, path_to_config: str):

        with open(path_to_config, 'r') as stream:
            self.config_params = yaml.safe_load(stream)

    def __enter__(self) -> psycopg.cursor:
        self.conn = psycopg.connect(**self.config_params)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()  
        self.conn.close()