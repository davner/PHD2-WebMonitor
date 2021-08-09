import os

# Configuration for python logging module
LOGGING_FILENAME = 'phdweb.log'
LOGGING_FILEPATH = '.'
LOGGING_DISABLE_EXISTING_LOGGERS = True
LOGGING_NAME = 'phdweb'
# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGGING_FILE_LEVEL = 'INFO'
LOGGING_STREAM_LEVEL = 'INFO'

# Don't change
LOGGING = {
    'version': 1,
    'disable_existing_loggers': LOGGING_DISABLE_EXISTING_LOGGERS,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s,%(levelname)s,%(name)s,%(funcName)s,%(message)s'
        },
        'basic': {
            'format': '%(asctime)-25s %(name)-30s %(levelname)-10s %(funcName)-20s %(message)s'
        }
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
            'level': LOGGING_STREAM_LEVEL,
            'stream': 'ext://sys.stdout'
        },
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'level': LOGGING_FILE_LEVEL,
            'filename': os.path.join(LOGGING_FILEPATH, LOGGING_FILENAME),
            'maxBytes': 1000000000000,
            'backupCount': 5
        }
    },
    'loggers': {
        '': {  # Root logger
            'level': 'DEBUG',
            'handlers': [
                'stream_handler',
                'file_handler'
            ]
        }
    }
}
