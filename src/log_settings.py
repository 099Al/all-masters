import logging
import logging.config
import os
import sys

LOG_FILE = 'logs/all-masters-app.log'
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s - %(asctime)s - %(name)s - %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'formatter': 'default',
            'filename': LOG_FILE,
            'mode': 'a',
            'encoding': 'utf8',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console'],
    },
}


logging.config.dictConfig(LOGGING_CONFIG)
