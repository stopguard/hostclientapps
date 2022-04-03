from functools import wraps
import logging
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
import log.client_log_config
import log.server_log_config


CLIENT_LOGGER = logging.getLogger('client')
SERVER_LOGGER = logging.getLogger('server')


def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        func_module = func.__module__
        func_caller = sys._getframe().f_back.f_code.co_name
        logger = CLIENT_LOGGER if 'client.py' in sys.argv[0] else SERVER_LOGGER
        logger.debug(f'Calling [{func_name}] from function [{func_caller}] with args: {args}; kwargs: {kwargs}')
        result = func(*args, **kwargs)
        logger.debug(f'[{func_module}.{func_name}] successfully completed. Returned results: {result}')
        return result
    return wrapper
