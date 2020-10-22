import unittest
import json

from api.main import app, set_mock_db


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        set_mock_db()
        self.app = app.test_client()

    def test_post_expression(self):
        rv = self.app.post('/api/expression', headers={"Content-Type": "application/json"},
                           data=json.dumps({
                               "expression": "x**2-5*x+6",
                               "variables": {"x": 3}
                           }))
        self.assertEqual(json.loads(rv.data)['expression_id'], 1)

        rv = self.app.post('/api/expression', headers={"Content-Type": "application/json"},
                           data=json.dumps({
                               "expression": "x+y",
                               "variables": {"x": 3} #missing 'y' value in variables
                           }))
        self.assertEqual(json.loads(rv.data)[
                         'msg'], 'JSON["variables"] does not match with variables in expression')

        rv = self.app.post('/api/expression', headers={}, #missing Content-Type header
                           data=json.dumps({
                               "expression": "x",
                               "variables": {"x": 3} 
                           }))
        self.assertEqual(json.loads(rv.data)[
                         'msg'], 'No JSON found')

        rv = self.app.post('/api/expression', headers={"Content-Type": "application/json"}, 
                           data=json.dumps({
                               "expression": "x", #missing variables
                           }))
        self.assertEqual(json.loads(rv.data)[
                         'msg'], 'JSON has a wrong structure')

        rv = self.app.post('/api/expression', headers={"Content-Type": "application/json"}, 
                           data=json.dumps({
                               "expression": "x;++", 
                               "variables": {"x": 3} 
                           }))
        self.assertEqual(json.loads(rv.data)[
                         'msg'], 'Error occured while parsing expression')

    def test_get_result(self):
        rv = self.app.get('/api/result/12')
        self.assertEqual(json.loads(rv.data)['result'], 1.0)   

        rv = self.app.get('/api/result/ffff')
        self.assertEqual(json.loads(rv.data)[
                         'msg'], 'Wrong URL: "expression_id" should be an integer')


if __name__ == '__main__':
    unittest.main()
