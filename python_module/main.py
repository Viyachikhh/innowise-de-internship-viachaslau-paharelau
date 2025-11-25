from db.db_query_exec import DatabaseQueryExecutor
from db.consts import PREDEFINED_SELECT_SQL_QUERIES
from db.db_init import * 
from db.db_load import *
from db.db_query_exec import * 


def main():
	executor = DatabaseQueryExecutor('postgresql.yaml')

	rooms_init(executor.connection)
	load_rooms_data(executor.connection)

	students_init(executor.connection)
	load_students_data(executor.connection)

	executor(PREDEFINED_SELECT_SQL_QUERIES['task_1'], 'task_1')
	executor(PREDEFINED_SELECT_SQL_QUERIES['task_2'], 'task_2')
	executor(PREDEFINED_SELECT_SQL_QUERIES['task_3'], 'task_3')
	executor(PREDEFINED_SELECT_SQL_QUERIES['task_4'], 'task_4')


if __name__ == "__main__":
	main()