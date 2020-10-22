from abc import abstractmethod


class Database(object):
    def __init__(self, dbname):
        self._dbname = dbname

    @property
    def dbname(self):
        return self._dbname

    @abstractmethod
    def execute_query(self, query, params):
        pass

    @abstractmethod
    def put_task(self, expression, variables):
        pass

    @abstractmethod
    def get_result(self, expression_id):
        pass

    @abstractmethod
    def get_tasks(self, num_tasks):
        pass

    @abstractmethod
    def insert_result_and_clean_queue(self, expression_results):
        pass
