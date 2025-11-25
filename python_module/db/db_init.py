from db.context import DatabaseConnection
from db.consts import SQL_TABLE_CREATE


def rooms_init(db_connection: DatabaseConnection, table_name='rooms', schema_name='information_schema.tables'):

        """
        Проверка на существование таблицы и её инициализация в случае отсутствия
        """

        with db_connection as cursor:
            sql_check_exists = f"select exists (select * from {schema_name} where table_name = %s)"""
            if not cursor.execute(sql_check_exists, (table_name, )).fetchone()[0]:
                cursor.execute(SQL_TABLE_CREATE[table_name])


def students_init(db_connection: DatabaseConnection, table_name='students', schema_name='information_schema.tables'):

        """
        Проверка на существование таблицы и её инициализация в случае отсутствия
        """

        with db_connection as cursor:
            sql_check_exists = f"select exists (select * from {schema_name} where table_name = %s)"""
            if not cursor.execute(sql_check_exists, (table_name, )).fetchone()[0]:
                cursor.execute(SQL_TABLE_CREATE[table_name]) 