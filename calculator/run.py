import repackage
repackage.up()

import settings
from calculator import run 

import logging 


logger = logging.getLogger(__name__)


def setup_logging(debug=False):
    logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(format=logging_format, level=level)
    
if __name__ == "__main__": 
    setup_logging(debug=settings.DEBUG)
    run()
