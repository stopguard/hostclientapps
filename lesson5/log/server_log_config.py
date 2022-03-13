import logging
import logging.handlers as handlers
import os

# setting up handler
log_path = os.path.join(os.getcwd(), 'server_logs', 'server_log.log')
handler = handlers.TimedRotatingFileHandler(log_path, when='midnight', encoding='utf-8')
handler.setLevel(1)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)

# setting up logger
server_logger = logging.getLogger('server')
server_logger.setLevel(1)
server_logger.addHandler(handler)


if __name__ == '__main__':
    server_logger.debug('debug')
    server_logger.info('info')
    server_logger.warning('warning')
    server_logger.error('error')
    server_logger.critical('critical')
