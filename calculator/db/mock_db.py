from .db import Database


class MockDB(Database):
    def __init__(self, dbname):
        self._dbname = dbname

    @property
    def dbname(self):
        return self._dbname

    def execute_query(self, query, params):
        assert str(query)
        assert dict(params)

    def put_task(self, expression, variables):
        assert str(expression)
        assert dict(variables)
        return [{'expression_id': 1}]

    def get_result(self, expression_id):
        assert int(expression_id)
        return [{'result': 1.0, 'error_code': 0}]

    def get_tasks(self, num_tasks):
        assert int(num_tasks)
        tasks = [{'expression_id': i, 'expression': 'a+1',
                  'variables': {'a': 1}} for i in range(1, num_tasks + 1)]
        return tasks

    def insert_result_and_clean_queue(self, expression_results):
        for res in expression_results:
            assert int(res[0])
            assert str(res[1])
            assert str(res[2])
            assert res[4] is int(res[4]) 
   
    def migrate(self):
        pass 