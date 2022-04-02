import logging
import socket
import sys
from argparse import ArgumentParser
from select import select
from time import time

import common.settings as consts
import log.server_log_config
from common.utils import get_data, post_data


# server logger init
SERVER_LOGGER = logging.getLogger('server')


def data_handler(data: dict) -> (dict, bool):
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
        message_text = data.get(consts.MESSAGE_TEXT)
        is_basic_checked = time_str and account_name
        if action == consts.PRESENCE and is_basic_checked:
            SERVER_LOGGER.info(f"Correct [{action}] from [{account_name}] received")
            result = {
                consts.RESPONSE: 200,
                consts.TIME: time(),
                consts.ALERT: 'OK',
            }
            return result, True
        elif action == consts.MESSAGE and is_basic_checked and message_text:
            result = {
                consts.ACTION: consts.MESSAGE,
                consts.SENDER: account_name,
                consts.TIME: time(),
                consts.MESSAGE_TEXT: message_text,
            }
            return result, False
        SERVER_LOGGER.warning(f'Incorrect request received: {data}')
    result = {
        consts.RESPONSE: 400,
        consts.TIME: time(),
        consts.ERROR: 'Bad request',
    }
    return result, True


def extract_args():
    argv = sys.argv[1:]
    SERVER_LOGGER.debug(f'Server app started with args: {argv}')
    parser = ArgumentParser()
    parser.add_argument('-a', '--ip', default='0.0.0.0', nargs='?')
    parser.add_argument('-p', '--port', default=consts.DEFAULT_SERVER_PORT, type=int, nargs='?')
    args = parser.parse_args(argv)
    listen_ip = args.ip
    listen_port = args.port if 1024 < args.port < 65535 else consts.DEFAULT_SERVER_PORT
    return listen_ip, listen_port


def main():
    listen_ip, listen_port = extract_args()

    SERVER_LOGGER.debug(f'Initiating listen address: {listen_ip}:{listen_port}.')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((listen_ip, listen_port))
        server_sock.listen()
        server_sock.settimeout(0.25)

        SERVER_LOGGER.info(f'Socket successfully created. Listen address: {listen_ip}:{listen_port}.')

        client_socks = []
        data_to_send = []

        while True:
            try:
                client_sock, client_address = server_sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.debug(f'Connection request from {client_address} received')
                client_socks.append(client_sock)

            senders_list = []
            listeners_list = []
            try:
                if client_socks:
                    senders_list, listeners_list, _ = select(client_socks, client_socks, [], 0)
            except OSError:
                pass

            if senders_list:
                for client_sock in senders_list:
                    try:
                        client_data = get_data(client_sock)
                        SERVER_LOGGER.debug(f'Received data from client {client_address}: {client_data}')
                        processed_data, is_direct = data_handler(client_data)
                        if is_direct:
                            post_data(processed_data, client_sock)
                            continue
                        data_to_send.append(processed_data)
                    except Exception as err:
                        SERVER_LOGGER.warning(f'Wrong data from client {client_address}. '
                                              f'Connect dropped. Exception: {err}')
                        client_sock.close()
                        client_socks.remove(client_sock)

            if data_to_send and listeners_list:
                current_data = data_to_send[0]
                for current_listener in listeners_list:
                    try:
                        post_data(current_data, current_listener)
                    except Exception as err:
                        SERVER_LOGGER.warning(f'Client {current_listener.getpeername()} disconnected from the server. '
                                              f'Error: {err}')
                        client_socks.remove(current_listener)
                        current_listener.close()
                del data_to_send[0]


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        SERVER_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
