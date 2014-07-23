<<<<<<< HEAD
import logging


def make_logger(loggerName, filename):
=======
#!/usr/bin/python

import logging
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('setting')
parser.add_argument('-v', '--verbosity', type=int)
ARGS = parser.parse_args()


def make_logger(loggerName, filename):

>>>>>>> ca2fe7b81228874d468b32f02671c968d710827a
    # create logger with 'spam_application'
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(filename)
<<<<<<< HEAD
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
=======
    fh.setLevel(logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    if ARGS.verbosity == 4:
        ch.setLevel(logging.DEBUG)
    elif ARGS.verbosity == 3:
        ch.setLevel(logging.INFO)
    elif ARGS.verbosity == 2:
        ch.setLevel(logging.WARNING)
    elif ARGS.verbosity == 1:
        ch.setLevel(logging.ERROR)
    else:
        ch.setLevel(logging.CRITICAL)# in case there is an issue with env variable
>>>>>>> ca2fe7b81228874d468b32f02671c968d710827a

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
<<<<<<< HEAD
=======


>>>>>>> ca2fe7b81228874d468b32f02671c968d710827a
