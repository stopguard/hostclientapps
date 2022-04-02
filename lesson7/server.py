import logging
import socket
import sys
from time import time

import common.settings as consts
import log.server_log_config
from common.utils import get_data, post_data


# server logger init
SERVER_LOGGER = logging.getLogger('server')


def data_handler(data: dict) -> dict:
    """
    handle received data
    :param data: received data
    :return: response data to send
    """
    try:
        action = data.get(consts.ACTION)
    except AttributeError as err:
        SERVER_LOGGER.error(f'Received data is not dict: {data}\n({err})')
    else:
        time_str = data.get(consts.TIME)
        account_name = data.get(consts.USER, {}).get(consts.ACCOUNT_NAME)
        if action == consts.PRESENCE and time_str and account_name:
            SERVER_LOGGER.info(f"Correct [{action}] from [{account_name}] received")
            return {
                consts.RESPONSE: 200,
                consts.TIME: time(),
                consts.ALERT: 'OK',
            }
        SERVER_LOGGER.warning(f'Incorrect request received: {data}')
    return {
        consts.RESPONSE: 400,
        consts.TIME: time(),
        consts.ERROR: 'Bad request',
    }


def main():
    args = sys.argv
    SERVER_LOGGER.debug(f'Server app started with args: {args}')

    port_idx_arg = None
    ip_idx_arg = None
    for i, arg in enumerate(args):
        if arg == '-p':
            port_idx_arg = i + 1
        if arg == '-a':
            ip_idx_arg = i + 1
    port_str = args[port_idx_arg] if port_idx_arg and len(args) >= port_idx_arg else consts.DEFAULT_SERVER_PORT
    server_port = int(port_str) if port_str.isdigit() and 1024 < int(port_str) < 65535 else consts.DEFAULT_SERVER_PORT
    server_ip = args[ip_idx_arg] if ip_idx_arg and len(args) >= ip_idx_arg else ''

    SERVER_LOGGER.debug(f'Initiating listen address: {server_ip or "0.0.0.0"}:{server_port}.')

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((server_ip, server_port))
    server_sock.listen()

    SERVER_LOGGER.info(f'Socket successfully created. Listen address: {server_ip or "0.0.0.0"}:{server_port}.')

    while True:
        client_sock, client_address = server_sock.accept()
        try:
            client_data = get_data(client_sock)
            SERVER_LOGGER.debug(f'Received data from client {client_address}: {client_data}')
            response = data_handler(client_data)
            post_data(response, client_sock)
            client_sock.close()
        except Exception as err:
            SERVER_LOGGER.error(f'Wrong data from client {client_address}. Exception: {err}')
            client_sock.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        SERVER_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
