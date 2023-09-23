# Standard library imports
import logging
from time import time


class Process:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')  # Basic config to logs

    def elapsed(self, func):
        def wrapper_function():
            start = time()
            func()
            end = time()
            logging.debug(f'The execution time: {end - start}')
        return wrapper_function
