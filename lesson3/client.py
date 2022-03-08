import socket
import sys
from time import time

import common.settings as consts
from common.utils import get_data, post_data


def presence(username: str) -> dict:
    """
    Generate PRESENCE data
    :param username: sender's username
    :return: data to send
    """
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
    status_code = response_data.get(consts.RESPONSE, 0)
    if status_code:
        result_msg = response_data.get(consts.ALERT, 'OK') \
            if status_code == 200 else \
            response_data.get(consts.ERROR, 'unknown error')
        return f'{status_code}: {result_msg}'
    return f'Wrong data'


def main():
    args_count = len(sys.argv)

    server_ip = sys.argv[1] if args_count >= 2 else consts.DEFAULT_SERVER_IP

    port_arg_check = args_count > 2 and sys.argv[2].isdigit() and 1024 < int(sys.argv[2]) < 65535
    server_port = int(sys.argv[2]) if port_arg_check else int(consts.DEFAULT_SERVER_PORT)

    print(f'Server address: {server_ip}:{server_port}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    data_to_send = presence('Guest')
    post_data(data_to_send, sock)
    try:
        response = get_data(sock)
        response = response_handler(response)
        print(response)
    except Exception as e:
        print(f'Wrong response. Exception: {e}')


if __name__ == '__main__':
    main()
