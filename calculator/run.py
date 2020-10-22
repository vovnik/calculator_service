import logging 

import db.postgres as pg
from calculator.calculator import Calculator 
from settings import *


logger = logging.getLogger(__name__)

db = pg.Postgres(dbname=DB_NAME, user=DB_USER,
                 password=DB_PASSWORD,
                 host=DB_HOST,
                 port=DB_PORT)



def setup_logging(debug=False):
    logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(format=logging_format, level=level)
    
if __name__ == "__main__": 
    setup_logging(debug=DEBUG)
    calculator = Calculator(db)
    calculator.run()
