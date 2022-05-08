import logging
import logging.handlers as handlers
import os

is_self_run = __name__ == '__main__'

# setting up handler
ending = ('server_log.log', ) if is_self_run else ('server_side', 'log', 'server_log.log')
log_path = os.path.join(os.getcwd(), *ending)
handler = handlers.TimedRotatingFileHandler(log_path, when='midnight', encoding='utf-8')
handler.setLevel(1)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)

# setting up logger
server_logger = logging.getLogger('server')
server_logger.setLevel(1)
server_logger.addHandler(handler)


if is_self_run:
    server_logger.debug('debug')
    server_logger.info('info')
    server_logger.warning('warning')
    server_logger.error('error')
    server_logger.critical('critical')
