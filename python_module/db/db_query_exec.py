import json

from db.context import DatabaseConnection


class DatabaseQueryExecutor:

    def __init__(self, path_to_config):
        self.__connection = DatabaseConnection(path_to_config=path_to_config)

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, another_config_path: str):
        self.__connection = DatabaseConnection(path_to_config=another_config_path)

    @connection.deleter
    def connection(self):
        del self.__connection

    def __call__(self, sql_query: str, sql_result_name: str):

        with self.__connection as cursor:
            cursor.execute(sql_query)
            column_names = [desc[0] for desc in cursor.description]
            result = cursor.fetchall()
        
        result = [{column_names[i]: row[i] for i in range(len(column_names))} for row in result]

        with open('result/' + sql_result_name + '.json', 'w') as file:
            json.dump(result, file)
                
