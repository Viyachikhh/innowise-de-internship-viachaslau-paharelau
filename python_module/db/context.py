import os
import psycopg



class DatabaseConnection:
    """
    Менеджер контекста для работы с базой данных в PostgreSQL
    """

    def __init__(self):
        self.dbname=os.getenv("POSTGRES_DB")
        self.user=os.getenv("POSTGRES_USER")
        self.password=os.getenv("POSTGRES_PASSWORD")
        self.host=os.getenv("POSTGRES_HOST")
        self.port=os.getenv("POSTGRES_PORT")
    

    def __enter__(self) -> psycopg.cursor:
        print(self.dbname)
        self.conn = psycopg.connect(dbname=self.dbname,
                                    user=self.user,
                                    password=self.password,
                                    host=self.host,
                                    port=self.port)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()  
        self.conn.close()