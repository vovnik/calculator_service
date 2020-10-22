from multiprocessing import Pool, Queue
import time
import json
import signal
import logging


from py_expression_eval import Parser

import db.postgres as pg
from settings import * 



logger = logging.getLogger(__name__)

result_queue = Queue()

db = pg.Postgres(dbname=DB_NAME, user=DB_USER,
                 password=DB_PASSWORD,
                 host=DB_HOST,
                 port=DB_PORT)


def signal_handler(signum, frame):
    raise TimeoutError("Calculation takes to long!")


def calculate_worker(task):
    logger.debug('Calculate task: ', task)
    parser = Parser()
    expression_id = task['expression_id']
    expression = task['expression']
    variables = task['variables']

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(CALCULATION_TIMEOUT)

    try:
        result = parser.parse(expression).evaluate(variables)
        error_code = 0
    except ZeroDivisionError:
        result = None
        error_code = 1 #ZeroDivisionError
    except OverflowError:
        result = None
        error_code = 2 #OverflowError
    except TimeoutError:
        result = None
        error_code = 3 #Calculation TimeoutError
    except Exception as e:
        logger.warning(f"Unexpected error while calculating task: {task}; error: ", e)
        result = None
        error_code = 4 #UnexpectedError
    finally:
        signal.alarm(0)

    res = (expression_id,
           expression,
           json.dumps(variables),
           result,
           error_code)
    result_queue.put(res)


def run():
    while True:
        logger.info(DB_HOST)
        tasks = db.get_tasks(TASK_NUM, DELAY_SEC)
        logger.debug(f'Got {len(tasks)} tasks')
        if len(tasks) == 0:
            time.sleep(QUEUE_WAIT_TIME)
            continue
        # in case 'get_tasks' gets db error
        if not tasks[0].get('expression'):
            time.sleep(QUEUE_WAIT_TIME)
            continue

        with Pool(processes=NUM_PROCESSES) as pool:
            pool.map(calculate_worker, tasks)
        results = []
        while not result_queue.empty():
            res = result_queue.get()
            results.append(res)
        logger.debug(f'Calculated {len(results)} tasks')
        if len(results) == 0:
            continue
        db.insert_result_and_clean_queue(results)
