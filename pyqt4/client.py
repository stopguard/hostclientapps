import logging
import socket
import sys
from argparse import ArgumentParser
from threading import Thread
from time import time, sleep

import common.settings as consts
import log.client_log_config
from common.metaclasses import ClientMaker
from common.utils import get_data, post_data

# client logger init
CLIENT_LOGGER = logging.getLogger('client')


class Client(metaclass=ClientMaker):
    def __init__(self):
        self.username = None
        self.server_sock = None
        self.sender_daemon = None
        self.reader_daemon = None

    def start(self, server_ip, server_port, username):
        self.username = username
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_sock:

            # connection block
            try:
                self.server_sock.connect((server_ip, server_port))
                CLIENT_LOGGER.info(f'Connected to server address: {server_ip}:{server_port}')
            except ConnectionRefusedError as err:
                CLIENT_LOGGER.critical(f"Can't connect to {server_ip}:{server_port}: {err}")
                exit(1)

            # authorisation block
            print(f'Connecting to {server_ip}:{server_port} as {self.username}')
            data_to_send = self.presence()
            post_data(data_to_send, self.server_sock)
            try:
                response = get_data(self.server_sock)
                response = self.response_handler(response)
                CLIENT_LOGGER.debug(f'Response processing result: {response}')
            except Exception as err:
                CLIENT_LOGGER.error(f'Wrong response. Exception: {err}')
                exit(1)

            CLIENT_LOGGER.info(f'Connected to {server_ip}:{server_port} as {self.username}')

            # services block
            self.run_daemons()
            self.main_cycle()

    def run_daemons(self):
        self.sender_daemon = Thread(target=self.sender_cycle)
        self.sender_daemon.daemon = True
        self.sender_daemon.start()
        CLIENT_LOGGER.info(f'Sender daemon [{self.username}] UP')

        self.reader_daemon = Thread(target=self.reader_cycle)
        self.reader_daemon.daemon = True
        self.reader_daemon.start()
        CLIENT_LOGGER.info(f'Receiver daemon [{self.username}] UP')

    def main_cycle(self):
        while True:
            sleep(1)
            if not self.reader_daemon.is_alive() or not self.sender_daemon.is_alive():
                break

    def sender_cycle(self):
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
                post_data(self.create_message(message), self.server_sock)
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as err:
                CLIENT_LOGGER.critical(f'Connection to server has dropped: {err}')
                exit(1)

    def reader_cycle(self):
        while True:
            try:
                self.print_message(get_data(self.server_sock))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as err:
                CLIENT_LOGGER.critical(f'Connection to server has dropped: {err}')
                exit(1)

    def presence(self) -> dict:
        """
        Generate PRESENCE data
        :return: data to send
        """
        CLIENT_LOGGER.debug(f'Creating presence message from {self.username}')
        return {
            consts.ACTION: consts.PRESENCE,
            consts.USER: {consts.ACCOUNT_NAME: self.username},
            consts.TIME: time(),
        }

    def create_message(self, msg_text: str) -> dict:
        split_msg = msg_text.split('/p/', 1)
        data = {
            consts.ACTION: consts.MESSAGE,
            consts.USER: {consts.ACCOUNT_NAME: self.username},
            consts.TIME: time(),
            consts.MESSAGE_TEXT: split_msg[-1].strip(),
        }
        CLIENT_LOGGER.debug(f'Message dict created: {data}')
        if len(split_msg) > 1:
            data[consts.RECIPIENT] = split_msg[0].strip()
        return data

    def print_message(self, data: dict):
        action = data.get(consts.ACTION)
        sender = data.get(consts.SENDER, False)
        sender = consts.YOU if sender == self.username else sender
        recipient = data.get(consts.RECIPIENT, False)
        recipient = consts.YOU if recipient == self.username else recipient
        message = data.get(consts.MESSAGE_TEXT, False)
        if action == consts.MESSAGE and sender and recipient and message:
            print(f'\n[{sender}] write to [{recipient}]: {message}')
            CLIENT_LOGGER.info(f'Received message from [{sender}] to [{recipient}]: {message}')
        else:
            CLIENT_LOGGER.error(f'Receive wrong message data from server: {data}')

    @staticmethod
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


if __name__ == '__main__':
    client = Client()
    try:
        client.start(*extract_args())
    except Exception as e:
        CLIENT_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
