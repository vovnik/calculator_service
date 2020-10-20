from os import environ

DEBUG = environ.get('DEBUG', 1)

CONNECT_NEXT_ATTEMPT = environ.get('CONNECT_NEXT_ATTEMPT', 10)
CONNECT_ATTEMPTS = environ.get('CONNECT_ATTEMPTS', 10)

TASK_NUM = environ.get('TASK_NUM', 20)
QUEUE_WAIT_TIME = environ.get('QUEUE_WAIT_TIME', 5)
CALCULATION_TIMEOUT = environ.get('CALCULATION_TIMEOUT', 10)
NUM_PROCESSES = environ.get('NUM_PROCESSES', 4)

DELAY_SEC = CALCULATION_TIMEOUT * TASK_NUM # set delay time for task to be processed again

DB_HOST = environ.get('DH_HOST', 'localhost')
DB_PORT = environ.get('DB_PORT', 5432)
DB_USER = environ.get('DH_USER', 'postgres')
DB_PASSWORD = environ.get('DH_PASSWORD', '12345')
DB_NAME = environ.get('DH_NAME', 'calculator_queue_tasks')
