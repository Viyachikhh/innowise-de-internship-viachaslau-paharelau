import json

from db.context import DatabaseContext
from db.db_abstract import AbstractStudents
from db.consts import SQL_TABLE_CREATE


class StudentsDatabase(AbstractStudents):

    def __init__(self, path_to_config):

        self.cursor = DatabaseContext(path_to_config=path_to_config)

        # создание таблиц, если их нет
        self.initialize_table('rooms')
        self.initialize_table('students')


    def load_data(self, source_data_path: str, destination_table_name: str):
        
        """
        Загрузка данных из файла в таблицы базы данных
        """

        with open(source_data_path, 'r') as file:
            data = json.load(file)

        # извлечение имён полей таблицы на основе файла
        columns = list(data[0].keys())

        placeholders = ' (' + ', '.join(['%s'] * len(columns)) + ');'

        columns = ', '.join(columns)
        columns = ' (' + columns + ') '

        data = [tuple([row[key] for key in row.keys()]) for row in data]
        with self.cursor as cursor:
            sql_insert = 'INSERT INTO ' + destination_table_name + columns + 'VALUES' + placeholders
            cursor.executemany(sql_insert, data)

    
    def select_query(self, sql_query: str):
        
        """
        Функция для выполнения select запроса для базы данных
        """

        with self.cursor as cursor:
            cursor.execute(sql_query)
            column_names = [desc[0] for desc in cursor.description]
            result = cursor.fetchall()
        
        result = [{column_names[i]: row[i] for i in range(len(column_names))} for row in result]

        return json.dumps(result)
    
    
    def initialize_table(self, table_name: str, schema_name='information_schema.tables'):

        """
        Проверка на существование таблицы и её инициализация в случае отсутствия
        """

        with self.cursor as cursor:
            sql_check_exists = f"select exists (select * from {schema_name} where table_name = %s)"""
            if not cursor.execute(sql_check_exists, (table_name, )).fetchone()[0]:
                cursor.execute(SQL_TABLE_CREATE[table_name])
                
