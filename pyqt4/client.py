import json
import logging
import socket
import sys
from argparse import ArgumentParser
from pprint import pprint
from threading import Thread, Lock
from time import time, sleep

import common.settings as consts
import log.client_log_config
from common.client_db import Storage
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
        self.db = None
        self.lock = Lock()

    def start(self, server_ip, server_port, username):
        self.username = username
        self.db = Storage(consts.CLIENT_DB, username)
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
            self.presence()
            self.refresh_contacts()

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
            message = input('Message (send /h for help): ').strip()
            if not message:
                print("can't send empty message!")
                CLIENT_LOGGER.warning(f'prevent send empty message')
                continue

            with self.lock:
                if message in consts.HELP_KEYS:
                    print(consts.CLIENT_HELP)
                elif message in consts.REFRESH_CONTACTS_KEYS:
                    self.refresh_contacts()
                elif message in consts.GET_CONTACTS_KEYS:
                    self.get_contacts()
                elif message[:len(consts.CONTACTS_ADD_KEY)] == consts.CONTACTS_ADD_KEY \
                        or message[:len(consts.CONTACTS_DEL_KEY)] == consts.CONTACTS_DEL_KEY:
                    self.edit_contact(message)
                else:
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

    def presence(self):
        CLIENT_LOGGER.debug(f'Creating presence message from {self.username}')
        request_data = {
            consts.ACTION: consts.PRESENCE,
            consts.USER: {consts.ACCOUNT_NAME: self.username},
            consts.TIME: time(),
        }
        post_data(request_data, self.server_sock)
        try:
            response = get_data(self.server_sock)
            status, message = self.response_handler(response)
            CLIENT_LOGGER.debug(f'Response PRESENCE result: {status}: {message}')
            if status and 200 <= status < 300:
                print('Successfully logged in')
                return
            raise Exception(f'{status}: {message}')
        except Exception as err:
            CLIENT_LOGGER.error(f'Wrong response. Exception: {err}')
            exit(1)

    def refresh_contacts(self):
        CLIENT_LOGGER.debug(f'Creating refresh contacts request from {self.username}')
        request_data = {
            consts.ACTION: consts.CONTACTS_GET,
            consts.TIME: time(),
            consts.USER: {consts.ACCOUNT_NAME: self.username},
        }
        post_data(request_data, self.server_sock)
        try:
            response = get_data(self.server_sock)
            status, message = self.response_handler(response)
            CLIENT_LOGGER.debug(f'Response REFRESH CONTACTS result: {status}: {message}')
            if status and 200 <= status < 300:
                print('Contacts received')
                self.db.refresh_contacts(json.loads(message))
                return
            print(f'{status}: {message}')
        except Exception as err:
            CLIENT_LOGGER.error(f'Wrong response. Exception: {err}')

    def edit_contact(self, command):
        action, contact_name = f'{command} '.split(' ', maxsplit=1)
        if not contact_name:
            log_msg = f'The [{action}] command requires a non-empty contact name!'
            print(log_msg)
            CLIENT_LOGGER.warning(log_msg)
        contact_name = contact_name.strip()
        action = consts.ACTIONS_DICT[action]
        CLIENT_LOGGER.debug(f'Creating [{action}] [{contact_name}] request from [{self.username}]')
        request_data = {
            consts.ACTION: action,
            consts.TIME: time(),
            consts.USER: {consts.ACCOUNT_NAME: self.username},
            consts.CONTACT_NAME: contact_name,
        }
        post_data(request_data, self.server_sock)
        try:
            response = get_data(self.server_sock)
            status, message = self.response_handler(response)
            CLIENT_LOGGER.debug(f'Response [{action}] [{contact_name}] result: {status}: {message}')
            print(f'{status}: {message}')
            if status and 200 <= status < 300:
                if action == consts.CONTACTS_ADD:
                    self.db.add_contact(contact_name)
                    return
                self.db.remove_contact(contact_name)
        except Exception as err:
            CLIENT_LOGGER.error(f'Wrong response. Exception: {err}')

    def get_contacts(self):
        pprint(self.db.get_contacts())

    def create_message(self, msg_text: str) -> dict:
        split_msg = msg_text.split(consts.PRIVATE_DELIMITER, 1)
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
        recipient = data.get(consts.RECIPIENT, False)
        processed_sender = consts.YOU if sender == self.username else sender
        processed_recipient = consts.YOU if recipient == self.username else recipient
        message = data.get(consts.MESSAGE_TEXT, False)
        if action == consts.MESSAGE and processed_sender and processed_recipient and message:
            print(f'\n[{processed_sender}] write to [{processed_recipient}]: {message}')
            with self.lock:
                self.db.add_to_history(sender, recipient, message)
            CLIENT_LOGGER.info(f'Received message from [{processed_sender}] to [{processed_recipient}]: {message}')
        else:
            CLIENT_LOGGER.error(f'Receive wrong message data from server: {data}')

    @staticmethod
    def response_handler(response_data: dict) -> tuple:
        """
        handle response data
        :param response_data: received data
        :return: response status and message
        """
        try:
            status_code = response_data.get(consts.RESPONSE, 0)
        except AttributeError as err:
            log_msg = f'Response data is not dict: {response_data}\n({err})\nResend request please'
        else:
            if status_code:
                if 200 <= status_code < 300:
                    result_msg = response_data.get(consts.ALERT, 'OK.')
                    CLIENT_LOGGER.info('Response status OK')
                else:
                    result_msg = response_data.get(consts.ERROR, 'unknown error')
                    CLIENT_LOGGER.warning(f'Warning! Response status: {status_code}: {result_msg}')
                return status_code, result_msg
            log_msg = f'Wrong data received: {response_data}'
        CLIENT_LOGGER.error(log_msg)
        return None, log_msg


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
