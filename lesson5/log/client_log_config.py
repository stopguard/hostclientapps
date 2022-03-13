import logging
import os

is_self_run = __name__ == '__main__'

# setting up handler
ending = ('client_logs', 'client_log.log') if is_self_run else ('log', 'client_logs', 'client_log.log')
log_path = os.path.join(os.getcwd(), *ending)
handler = logging.FileHandler(log_path, encoding='utf-8')
handler.setLevel(logging.NOTSET)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)

# setting up logger
client_logger = logging.getLogger('client')
client_logger.setLevel(logging.DEBUG)
client_logger.addHandler(handler)


if is_self_run:
    client_logger.debug('debug')
    client_logger.info('info')
    client_logger.warning('warning')
    client_logger.error('error')
    client_logger.critical('critical')
