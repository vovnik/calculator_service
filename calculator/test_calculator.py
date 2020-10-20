import unittest
import calculator.main as calc


class CalculatorTestCase(unittest.TestCase):

    def test_calculate_worker(self):
        task = {'expression_id': 1,
                'expression': 'a+1',
                'variables': {'a': 1}}
        calc.calculate_worker(task)
        res = calc.result_queue.get()
        self.assertEqual(res[4], 0) #check results error code 
        self.assertEqual(res[3], 2) #check result 
        
        task = {'expression_id': 2,
               'expression': 'a/0',
               'variables': {'a': 1}}
        calc.calculate_worker(task)
        res = calc.result_queue.get()
        self.assertEqual(res[4], 1)
        self.assertIsNone(res[3])  


        task = {'expression_id': 3,
               'expression': 'a*1000000000000000000**100000000',
               'variables': {'a': 1}}
        calc.calculate_worker(task)
        res = calc.result_queue.get()
        self.assertEqual(res[4], 2)
        self.assertIsNone(res[3])       


if __name__ == '__main__':
    unittest.main()
