from abc import ABC, abstractmethod


class AbstractStudents(ABC):

    @abstractmethod
    def __init__(self, path_to_config: str):
        pass

    @abstractmethod
    def load_data(self, source_data_path: str, destination_table_name: str):
        pass
    
    @abstractmethod
    def initialize_table(self, table_name: str, schema_name='information_schema.tables'):
        pass


