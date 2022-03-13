import logging
import os

# setting up handler
log_path = os.path.join(os.getcwd(), 'client_logs', 'client_log.log')
handler = logging.FileHandler(log_path, encoding='utf-8')
handler.setLevel(logging.NOTSET)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)

# setting up logger
client_logger = logging.getLogger('client')
client_logger.setLevel(logging.DEBUG)
client_logger.addHandler(handler)


if __name__ == '__main__':
    client_logger.debug('debug')
    client_logger.info('info')
    client_logger.warning('warning')
    client_logger.error('error')
    client_logger.critical('critical')
