import socket
import sys
import logging
from time import time

import common.settings as consts
from common.utils import get_data, post_data
import log.client_log_config


# client logger init
CLIENT_LOGGER = logging.getLogger('client')


def presence(username: str) -> dict:
    """
    Generate PRESENCE data
    :param username: sender's username
    :return: data to send
    """
    CLIENT_LOGGER.debug(f'Creating presence message from {username}')
    return {
        consts.ACTION: consts.PRESENCE,
        consts.USER: {consts.ACCOUNT_NAME: username},
        consts.TIME: time(),
    }


def response_handler(response_data: dict) -> str:
    """
    handle response data
    :param response_data: received data
    :return: response status string
    """
    try:
        status_code = response_data.get(consts.RESPONSE, 0)
    except AttributeError:
        CLIENT_LOGGER.error(f'Response data is not dict: {response_data}')
    else:
        if status_code:
            if status_code == 200:
                result_msg = response_data.get(consts.ALERT, 'OK.')
                CLIENT_LOGGER.info('Response status OK')
            else:
                result_msg = response_data.get(consts.ERROR, 'unknown error')
                CLIENT_LOGGER.warning(f'Warning! Response status: {status_code}: {result_msg}')
            return f'{status_code}: {result_msg}'
        CLIENT_LOGGER.error(f'Wrong data received: {response_data}')
        return 'Wrong data'


def main():
    args = sys.argv
    args_count = len(args)
    CLIENT_LOGGER.debug(f'Client app started with args: {args}')

    server_ip = args[1] if args_count >= 2 else consts.DEFAULT_SERVER_IP

    port_arg_check = args_count > 2 and args[2].isdigit() and 1024 < int(args[2]) < 65535
    server_port = int(args[2]) if port_arg_check else int(consts.DEFAULT_SERVER_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, server_port))
        CLIENT_LOGGER.info(f'Connected to server address: {server_ip}:{server_port}')
    except ConnectionRefusedError as e:
        CLIENT_LOGGER.critical(f"Can't connect to {server_ip}:{server_port}: {e}")

    data_to_send = presence('Guest')
    post_data(data_to_send, sock)
    try:
        response = get_data(sock)
        response = response_handler(response)
        CLIENT_LOGGER.debug(f'Response processing result: {response}')
    except Exception as e:
        CLIENT_LOGGER.error(f'Wrong response. Exception: {e}')


if __name__ == '__main__':
    main()
