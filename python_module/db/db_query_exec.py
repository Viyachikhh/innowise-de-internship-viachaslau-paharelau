import json

from db.context import DatabaseConnection


class DatabaseQueryExecutor:

    def __init__(self):
        self.__connection = DatabaseConnection()

    @property
    def connection(self):
        return self.__connection

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
                
        print('OK!')