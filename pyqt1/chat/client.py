import logging
import socket
import sys
from argparse import ArgumentParser
from threading import Thread
from time import time, sleep

import common.settings as consts
import log.client_log_config
from common.utils import get_data, post_data

# client logger init
CLIENT_LOGGER = logging.getLogger('client')


def extract_args():
    argv = sys.argv[1:]
    CLIENT_LOGGER.debug(f'Client app started with args: {argv}')
    parser = ArgumentParser()
    parser.add_argument('addr', default=consts.DEFAULT_SERVER_IP, nargs='?')
    parser.add_argument('port', default=consts.DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=consts.GUEST, nargs='?')
    args = parser.parse_args(argv)

    server_ip = args.addr
    server_port = args.port if 1024 < args.port < 65535 else consts.DEFAULT_SERVER_PORT
    client_name = args.name if args.name != consts.ALL else consts.GUEST
    return server_ip, server_port, client_name


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
    split_msg = msg_text.split('/p/', 1)
    data = {
        consts.ACTION: consts.MESSAGE,
        consts.USER: {consts.ACCOUNT_NAME: username},
        consts.TIME: time(),
        consts.MESSAGE_TEXT: split_msg[-1].strip(),
    }
    CLIENT_LOGGER.debug(f'Message dict created: {data}')
    if len(split_msg) > 1:
        data[consts.RECIPIENT] = split_msg[0].strip()
    return data


def print_message(data: dict, username: str):
    action = data.get(consts.ACTION)
    sender = data.get(consts.SENDER, False)
    sender = consts.YOU if sender == username else sender
    recipient = data.get(consts.RECIPIENT, False)
    recipient = consts.YOU if recipient == username else recipient
    message = data.get(consts.MESSAGE_TEXT, False)
    if action == consts.MESSAGE and sender and recipient and message:
        print(f'\n[{sender}] write to [{recipient}]: {message}')
        CLIENT_LOGGER.info(f'Received message from [{sender}] to [{recipient}]: {message}')
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
                print('Successfully logged in')
                CLIENT_LOGGER.info('Response status OK')
            else:
                result_msg = response_data.get(consts.ERROR, 'unknown error')
                CLIENT_LOGGER.warning(f'Warning! Response status: {status_code}: {result_msg}')
            return f'{status_code}: {result_msg}'
        CLIENT_LOGGER.error(f'Wrong data received: {response_data}')
    return 'Wrong data'


def sender_cycle(sock: socket.SocketType, username: str):
    while True:
        message = input('Message (send /h for help): ')
        if not message:
            print("can't send empty message!")
            CLIENT_LOGGER.warning(f'prevent send empty message')
            continue
        if message == '/h':
            print(consts.CLIENT_HELP)
            continue
        try:
            post_data(create_message(message, username), sock)
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as err:
            CLIENT_LOGGER.critical(f'Connection to server has dropped: {err}')
            exit(1)


def reader_cycle(sock: socket.SocketType, username: str):
    while True:
        try:
            print_message(get_data(sock), username)
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as err:
            CLIENT_LOGGER.critical(f'Connection to server has dropped: {err}')
            exit(1)


def main():
    server_ip, server_port, client_name = extract_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # connection block
        try:
            sock.connect((server_ip, server_port))
            CLIENT_LOGGER.info(f'Connected to server address: {server_ip}:{server_port}')
        except ConnectionRefusedError as err:
            CLIENT_LOGGER.critical(f"Can't connect to {server_ip}:{server_port}: {err}")
            exit(1)

        # authorisation block
        print(f'Connecting to {server_ip}:{server_port} as {client_name}')
        data_to_send = presence(client_name)
        post_data(data_to_send, sock)
        try:
            response = get_data(sock)
            response = response_handler(response)
            CLIENT_LOGGER.debug(f'Response processing result: {response}')
        except Exception as err:
            CLIENT_LOGGER.error(f'Wrong response. Exception: {err}')
            exit(1)

        CLIENT_LOGGER.info(f'Connected to {server_ip}:{server_port} as {client_name}')

        sender_thread = Thread(target=sender_cycle, args=(sock, client_name))
        sender_thread.daemon = True
        sender_thread.start()
        CLIENT_LOGGER.info(f'Sender daemon [{client_name}] UP')

        reader_thread = Thread(target=reader_cycle, args=(sock, client_name))
        reader_thread.daemon = True
        reader_thread.start()
        CLIENT_LOGGER.info(f'Receiver daemon [{client_name}] UP')

        while True:
            sleep(1)
            if not reader_thread.is_alive() or not sender_thread.is_alive():
                break


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        CLIENT_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
