from db.db_interface import StudentsDatabase
from db.consts import PREDEFINED_SELECT_SQL_QUERIES


if __name__ == "__main__":
	interface = StudentsDatabase('postgresql.yaml')
	interface.load_data('data/rooms.json', 'rooms')
	interface.load_data('data/students.json', 'students')

	# Это чисто для вывода результата
	result_1 = interface.select_query(PREDEFINED_SELECT_SQL_QUERIES['task_1'])
	result_2 = interface.select_query(PREDEFINED_SELECT_SQL_QUERIES['task_2'])
	result_3 = interface.select_query(PREDEFINED_SELECT_SQL_QUERIES['task_3'])
	result_4 = interface.select_query(PREDEFINED_SELECT_SQL_QUERIES['task_4'])