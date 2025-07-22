
#log_config.py

import logging
import os

LOG_FILE = 'logs/shop.log'
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)




