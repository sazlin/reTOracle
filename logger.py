#!/usr/bin/python
import os
import logging


def make_logger(loggerName, filename):
    verbosity = int(os.environ.get('R_LOGGING_LEVEL', 3))
    # create logger with 'spam_application'
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(filename)

    fh.setLevel(logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    if verbosity == 4:
        ch.setLevel(logging.DEBUG)
    elif verbosity == 3:
        ch.setLevel(logging.INFO)
    elif verbosity == 2:
        ch.setLevel(logging.WARNING)
    elif verbosity == 1:
        ch.setLevel(logging.ERROR)
    else:
        ch.setLevel(logging.CRITICAL)  # in case there is an issue with env variable

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
