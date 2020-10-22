from os import environ

DEBUG = int(environ.get('DEBUG', 1))

################################################################
# DB settings 
################################################################
CONNECT_NEXT_ATTEMPT = int(environ.get('CONNECT_NEXT_ATTEMPT', 10))
CONNECT_ATTEMPTS = int(environ.get('CONNECT_ATTEMPTS', 10))

DB_HOST = environ.get('DB_HOST', 'db_postgres')
DB_PORT = int(environ.get('DB_PORT', 4200))
DB_USER = environ.get('DB_USER', 'user')
DB_PASSWORD = environ.get('DB_PASSWORD', 'pass')
DB_NAME = environ.get('DB_NAME', 'postgres')
################################################################


