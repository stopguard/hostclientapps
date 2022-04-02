import logging
import socket
import sys
from argparse import ArgumentParser
from time import time

import common.settings as consts
import log.client_log_config
from common.utils import get_data, post_data

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


def create_message(msg_text: str, username: str) -> dict:
    data = {
        consts.ACTION: consts.MESSAGE,
        consts.USER: {consts.ACCOUNT_NAME: username},
        consts.TIME: time(),
        consts.MESSAGE_TEXT: msg_text,
    }
    CLIENT_LOGGER.debug(f'Message dict created: {data}')
    return data


def print_message(data: dict):
    action = data.get(consts.ACTION)
    sender = data.get(consts.SENDER, False)
    message = data.get(consts.MESSAGE_TEXT, False)
    if action == consts.MESSAGE and sender and message:
        print(f'[{sender}] write: {message}')
        CLIENT_LOGGER.info(f'Received message from [{sender}]: {message}')
    else:
        CLIENT_LOGGER.error(f'Receive wrong message data from server: {data}')


def response_handler(response_data: dict) -> str:
    """
    handle response data
    :param response_data: received data
    :return: response status string
    """
    try:
        status_code = response_data.get(consts.RESPONSE, 0)
    except AttributeError as err:
        CLIENT_LOGGER.error(f'Response data is not dict: {response_data}\n({err})\nResend request please')
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


def sender_cycle(sock: socket.SocketType, username: str):
    while True:
        message = input('Text for send: ')
        if not message:
            print("can't send empty message!")
            CLIENT_LOGGER.warning(f'prevent send empty message')
            continue
        try:
            post_data(create_message(message, username), sock)
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as err:
            CLIENT_LOGGER.critical(f'Connection to server has dropped: {err}')


def reader_cycle(sock: socket.SocketType):
    while True:
        try:
            print_message(get_data(sock))
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as err:
            CLIENT_LOGGER.critical(f'Connection to server has dropped: {err}')


def extract_args():
    argv = sys.argv[1:]
    CLIENT_LOGGER.debug(f'Client app started with args: {argv}')
    parser = ArgumentParser()
    parser.add_argument('addr', default=consts.DEFAULT_SERVER_IP, nargs='?')
    parser.add_argument('port', default=consts.DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='read', nargs='?')
    parser.add_argument('-n', '--name', default='Guest', nargs='?')
    args = parser.parse_args(argv)

    server_ip = args.addr
    server_port = args.port if 1024 < args.port < 65535 else consts.DEFAULT_SERVER_PORT
    is_sender = args.mode == 'send'
    client_name = args.name
    return server_ip, server_port, is_sender, client_name


def main():
    server_ip, server_port, is_sender, client_name = extract_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # connection block
        try:
            sock.connect((server_ip, server_port))
            CLIENT_LOGGER.info(f'Connected to server address: {server_ip}:{server_port}')
        except ConnectionRefusedError as err:
            CLIENT_LOGGER.critical(f"Can't connect to {server_ip}:{server_port}: {err}")
            exit(1)

        # authorisation block
        data_to_send = presence(client_name)
        post_data(data_to_send, sock)
        try:
            response = get_data(sock)
            response = response_handler(response)
            CLIENT_LOGGER.debug(f'Response processing result: {response}')
        except Exception as err:
            CLIENT_LOGGER.error(f'Wrong response. Exception: {err}')
            exit(1)

        if is_sender:
            CLIENT_LOGGER.info(f'Connected to {server_ip}:{server_port} as {client_name}(sender)')
            sender_cycle(sock, client_name)
        else:
            CLIENT_LOGGER.info(f'Connected to {server_ip}:{server_port} as {client_name}(reader)')
            reader_cycle(sock)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        CLIENT_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
