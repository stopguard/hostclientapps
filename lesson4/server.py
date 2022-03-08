import socket
import sys
from time import time

import common.settings as consts
from common.utils import get_data, post_data


def data_handler(data: dict) -> dict:
    """
    handle received data
    :param data: received data
    :return: response data to send
    """
    action = data.get(consts.ACTION)
    time_str = data.get(consts.TIME)
    account_name = data.get(consts.USER, {}).get(consts.ACCOUNT_NAME)
    if action == consts.PRESENCE and time_str and account_name == 'Guest':
        return {
            consts.RESPONSE: 200,
            consts.TIME: time(),
            consts.ALERT: 'OK',
        }
    return {
        consts.RESPONSE: 400,
        consts.TIME: time(),
        consts.ERROR: 'Bad request',
    }


def main():
    args = sys.argv
    port_idx_arg = None
    ip_idx_arg = None
    for i, arg in enumerate(args):
        if arg == '-p':
            port_idx_arg = i + 1
        if arg == '-a':
            ip_idx_arg = i + 1
    port_str = args[port_idx_arg] if port_idx_arg and len(args) >= port_idx_arg else consts.DEFAULT_SERVER_PORT
    print(f'Selected listen port: {port_str}.')
    server_port = int(port_str) if port_str.isdigit() and 1024 < int(port_str) < 65535 else consts.DEFAULT_SERVER_PORT
    server_ip = args[ip_idx_arg] if ip_idx_arg and len(args) >= ip_idx_arg else ''

    print(f'Initiated listen address: {server_ip or "0.0.0.0"}:{server_port}.')

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((server_ip, server_port))
    server_sock.listen()

    while True:
        client_sock, _ = server_sock.accept()
        try:
            client_data = get_data(client_sock)
            print(client_data)
            response = data_handler(client_data)
            post_data(response, client_sock)
            client_sock.close()
        except Exception as e:
            print('Wrong data. Exception:', e)
            client_sock.close()


if __name__ == '__main__':
    main()
