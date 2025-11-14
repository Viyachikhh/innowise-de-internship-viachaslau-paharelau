import json
import psycopg
import yaml


class DatabaseContext:

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


class StudentsDatabase:

    def __init__(self, path_to_config):
        self.__context_object__ = DatabaseContext(path_to_config=path_to_config)

        sql_create = """
        create table rooms (
	            rid serial primary key, 
	            rname varchar
                );

        create table students (
	            sid serial primary key,
	            birthday timestamp,
	            sname varchar,
	            room serial references rooms(rid) ON DELETE CASCADE ON UPDATE CASCADE,
	            sex char(1),
	            check (sex in ('F', 'M'))
                );
        
        create index r_number ON students (room);
        create index birthday ON students (birthday);
        """

        with self.__context_object__ as cursor:
            cursor.execute(sql_create)

    def load_rooms(self, rooms_path):

        """
        Загрузка номеров комнат из файла
        """

        with open(rooms_path, 'r') as r_file:
            rooms = json.load(r_file)

        rooms = [(row['id'], row['name']) for row in rooms]

        with self.__context_object__ as cursor:
            sql_query = 'INSERT INTO rooms (rid, rname) VALUES (%s, %s)'
            cursor.executemany(sql_query, rooms)

    def load_students(self, students_path: str):

        """
        Загрузка студентов из файла
        """

        with open(students_path, 'r') as s_file:
            students = json.load(s_file)
       
        students = [(row['id'],
                     row['birthday'], 
                     row['name'], 
                     row['room'], 
                     row['sex'], ) for row in students]

        with self.__context_object__ as cursor:
            sql_query = 'INSERT INTO students (sid, birthday, sname, room, sex) VALUES (%s, %s, %s, %s, %s)'
            cursor.executemany(sql_query, students)

    def select_query(self, sql_query: str, result_name: str):

        with self.__context_object__ as cursor:
            cursor.execute(sql_query)
            column_names = [desc[0] for desc in cursor.description]
            result = cursor.fetchall()
        
        result = [{column_names[i]: row[i] for i in range(len(column_names))} for row in result]

        # with open(result_name, 'w') as f:
        #     json.dump(result, f)

        return json.dumps(result)