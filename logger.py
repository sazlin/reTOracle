#!/usr/bin/python

import logging
import os


def set_level(logging='v'):

    if logging == 'vvvv':
        os.environ['LOGGING'] = 'Debug'
    elif logging == 'vvv':
        os.environ['LOGGING'] = 'Info'
    elif logging == 'vv':
        os.environ['LOGGING'] = 'Warning'
    else:
        os.environ['LOGGING'] = 'File'


def make_logger(loggerName, filename):
    # create logger with 'spam_application'
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    level = os.environ.get('LOGGING', None)
    if level == 'Debug':
        ch.setLevel(logging.DEBUG)
    elif level == 'Info':
        ch.setLevel(logging.INFO)
    elif level == 'Warning':
        ch.setLevel(logging.WARNING)
    elif level == 'File':
        ch.setLevel(logging.ERROR)
    else:
        ch.setLevel(logging.CRITICAL)# in case there is an issue with env variable

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
