import json
from db.context import DatabaseConnection


def load_rooms_data(db_connect: DatabaseConnection, data_path='data/rooms.json'):
        
        """
        Загрузка данных из файла в таблицу комнат 
        """

        with open(data_path, 'r') as file:
            data = json.load(file)

        # извлечение имён полей таблицы на основе файла
        columns = list(data[0].keys())

        placeholders = ' (' + ', '.join(['%s'] * len(columns)) + ');'

        columns = ', '.join(columns)
        columns = ' (' + columns + ') '

        data = [tuple([row[key] for key in row.keys()]) for row in data]

        with db_connect as cursor:
            sql_insert = 'INSERT INTO rooms ' + columns + 'VALUES' + placeholders

            sql_select_original_data = 'SELECT * FROM rooms;'
            cursor.execute(sql_select_original_data)
            original_data = cursor.fetchall()

            data_insert = set(data) - set(original_data) 
            # print('rooms', data_insert)
            if len(data_insert) > 0:

                data_insert = list(data_insert)
                cursor.executemany(sql_insert, data_insert)


def load_students_data(db_connect: DatabaseConnection, data_path='data/students.json'):
        
        """
        Загрузка данных из файла в таблицу студентов
        """

        with open(data_path, 'r') as file:
            data = json.load(file)

        # извлечение имён полей таблицы на основе файла
        columns = list(data[0].keys())

        placeholders = ' (' + ', '.join(['%s'] * len(columns)) + ');'

        columns = ', '.join(columns)
        columns = ' (' + columns + ') '

        data = [tuple([row[key] for key in row.keys()]) for row in data]

        with db_connect as cursor:
            sql_insert = 'INSERT INTO students ' + columns + 'VALUES' + placeholders

            cursor.executemany(sql_insert, data)