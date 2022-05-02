import logging
import socket
import sys
from argparse import ArgumentParser
from ipaddress import ip_address
from select import select
from time import time

import common.settings as consts
import log.server_log_config
from common.descriptors import IP, Port
from common.metaclasses import ServerMaker
from common.server_db import Storage
from common.utils import get_data, post_data

# server logger init
SERVER_LOGGER = logging.getLogger('server')


class Server(metaclass=ServerMaker):
    listen_ip = IP()
    port = Port()

    def __init__(self):
        self.client_socks = []
        self.authorised_socks = {}
        self.guest_socks = []
        self.listeners_list = []
        self.data_to_send = []
        self.socket = None
        self.listen_ip = ip_address('0.0.0.0')
        self.port = consts.DEFAULT_SERVER_PORT
        self.db = Storage(consts.SERVER_DB)
        self.actions = {
            consts.PRESENCE: self.presence,
            consts.MESSAGE: self.message,
            consts.CONTACTS_GET: self.get_contacts,
            consts.CONTACTS_ADD: self.add_contact,
            consts.CONTACTS_DEL: self.del_contact,
        }

    def start(self, listen_ip, port: int):
        SERVER_LOGGER.debug(f'Initiating listen address: {listen_ip}:{port}.')

        self.listen_ip = listen_ip
        self.port = port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((str(self.listen_ip), self.port))
            self.socket.listen()
            self.socket.settimeout(0.25)

            SERVER_LOGGER.info(f'Socket successfully created. Listen address: {self.listen_ip}:{self.port}.')
            self.main_cycle()

    def main_cycle(self):
        while True:
            try:
                client_sock, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.debug(f'Connection request from {client_address} received')
                self.client_socks.append(client_sock)

            senders_list = []
            self.listeners_list = []
            try:
                if self.client_socks:
                    senders_list, self.listeners_list, _ = select(self.client_socks, self.client_socks, [], 0)
            except OSError:
                pass

            if senders_list:
                for client_sock in senders_list:
                    try:
                        self.data_handler(client_sock)
                    except Exception as err:
                        ip, port = client_sock.getpeername()
                        SERVER_LOGGER.warning(f'Wrong data from client {ip}:{port}. '
                                              f'Connection dropped. Exception: {err}')
                        client_sock.close()
                        if client_sock in self.guest_socks:
                            self.guest_socks.remove(client_sock)
                        else:
                            for key, value in self.authorised_socks.items():
                                if value == client_sock:
                                    del self.authorised_socks[key]
                                    break
                        self.client_socks.remove(client_sock)
                        self.db.disconnect_user(ip=ip, port=port)

            if self.data_to_send and self.listeners_list:
                current_data = self.data_to_send[0]
                for current_listener in self.listeners_list:
                    try:
                        post_data(current_data, current_listener)
                    except Exception as err:
                        ip, port = current_listener.getpeername()
                        SERVER_LOGGER.warning(f'Client {ip}:{port} disconnected from the server. '
                                              f'Connection dropped. Exception: {err}')
                        if current_listener in self.guest_socks:
                            self.guest_socks.remove(current_listener)
                        else:
                            listener_key = False
                            for key, value in self.authorised_socks.items():
                                if value == current_listener:
                                    listener_key = key
                                    break
                            if listener_key:
                                del self.authorised_socks[listener_key]
                        self.db.disconnect_user(ip=ip, port=port)
                        self.client_socks.remove(current_listener)
                        current_listener.close()
                del self.data_to_send[0]

    def data_handler(self, client_sock: socket.SocketType):
        """
        handle received data
        :param client_sock: sender socket
        :returns: data to send, data type, recipient
        """
        data = get_data(client_sock)
        ip, port = client_sock.getpeername()
        SERVER_LOGGER.debug(f'Received data from client {ip}:{port}: {data}')
        error = consts.BAD_REQUEST
        log_string = f'Incorrect request received: {data}'
        if type(data) == dict:
            error = data.get(consts.ERROR) or error
            action = data.get(consts.ACTION)
            time_str = data.get(consts.TIME)
            account_name = data.get(consts.USER, {}).get(consts.ACCOUNT_NAME)
            if time_str and account_name and action in self.actions:
                self.actions[action](data, client_sock)
                return
        else:
            log_string = f'Received data is not dict: {data}'

        # Error response for incorrect requests
        self.error_handler(error, log_string, client_sock)

    def presence(self, data: dict, client_sock: socket.SocketType):
        account_name = data[consts.USER][consts.ACCOUNT_NAME]
        result = {
            consts.RESPONSE: 200,
            consts.TIME: time(),
            consts.ALERT: 'OK',
        }
        if account_name == consts.GUEST:
            self.guest_socks.append(client_sock)
        elif account_name != consts.ALL and account_name not in self.authorised_socks:
            self.authorised_socks[account_name] = client_sock
        else:
            self.error_handler(consts.INVALID_USERNAME, f'{consts.INVALID_USERNAME} in request {data}', client_sock)
            raise Exception(consts.INVALID_USERNAME)
        SERVER_LOGGER.info(f"Correct [{consts.PRESENCE}] from [{account_name}] received")
        post_data(result, client_sock)
        ip, port, *args = client_sock.getpeername()
        self.db.connect_user(account_name, ip, port)

    def message(self, data: dict, client_sock: socket.SocketType):
        message_text = data.get(consts.MESSAGE_TEXT)

        if message_text:
            sender_name = data[consts.USER][consts.ACCOUNT_NAME]
            recipient_name = consts.ALL if sender_name == consts.GUEST else data.get(consts.RECIPIENT, consts.ALL)
            SERVER_LOGGER.info(f"Correct [{consts.MESSAGE}] from [{sender_name}] received")
            sender_sock = self.authorised_socks.get(sender_name)
            target_sock = self.authorised_socks.get(recipient_name)
            is_sender_authorised = sender_sock == client_sock
            is_sender_guest = sender_name == consts.GUEST and client_sock in self.guest_socks
            SERVER_LOGGER.debug(f'msg attrs: {sender_name=}, {sender_sock=}, {target_sock=}, '
                                f'{is_sender_authorised=}, {is_sender_guest=}')
            sent_data = {
                consts.ACTION: consts.MESSAGE,
                consts.TIME: time(),
                consts.SENDER: sender_name,
                consts.RECIPIENT: recipient_name,
                consts.MESSAGE_TEXT: message_text,
            }

            # Drop unauthorised client
            if not is_sender_authorised and not is_sender_guest:
                self.error_handler(consts.INVALID_SENDER, f'sender {sender_name} is not authorised', client_sock)
                raise Exception(consts.INVALID_SENDER)

            # Private message
            elif is_sender_authorised and target_sock:
                SERVER_LOGGER.info(f'sender {sender_name} send private msg to {recipient_name}')
                try:
                    if target_sock not in self.listeners_list:
                        raise Exception('Lost connection to client')
                    post_data(sent_data, target_sock)
                    if sender_name != recipient_name:
                        post_data(sent_data, client_sock)
                    return
                except Exception as err:
                    ip, port = target_sock.getpeername()
                    SERVER_LOGGER.warning(f'Lost connection to {ip}:{port}. '
                                          f'Connection dropped. Exception: {err}')
                    target_sock.close()
                    self.db.disconnect_user(ip=ip, port=port)
                    self.client_socks.remove(target_sock)
                    del self.authorised_socks[recipient_name]

            # Global message
            elif recipient_name == consts.ALL:
                self.data_to_send.append(sent_data)
                return

            # Wrong recipient name
            sent_data.update({
                consts.SENDER: consts.SERVER,
                consts.RECIPIENT: sender_name,
                consts.MESSAGE_TEXT: f'{consts.INVALID_RECIPIENT} ({recipient_name})'
            })
            post_data(sent_data, client_sock)
            return

        # Empty message text
        self.error_handler(consts.BAD_REQUEST, f'Empty message text: {data}', client_sock)

    def get_contacts(self, data: dict, client_sock: socket.SocketType):
        client_name = data[consts.USER][consts.ACCOUNT_NAME]
        if client_name != consts.GUEST:
            contacts = self.db.get_contacts(client_name)
            response = {
                consts.RESPONSE: 200,
                consts.TIME: time(),
                consts.ALERT: contacts,
            }
            post_data(response, client_sock)
            return
        self.error_handler(consts.INVALID_USERNAME, f"Guests can't use contact list. Data: {data}", client_sock)

    def add_contact(self, data: dict, client_sock: socket.SocketType):
        client_name = data[consts.USER][consts.ACCOUNT_NAME]
        contact_name = data.get(consts.CONTACT_NAME)
        if client_name != consts.GUEST and contact_name and client_name != contact_name:
            self.db.add_contact(client_name, contact_name)
            response = {
                consts.RESPONSE: 202,
                consts.TIME: time(),
                consts.ALERT: 'OK',
            }
            post_data(response, client_sock)
            return
        self.error_handler(consts.INVALID_USERNAME,
                           f"Client is Guest or incorrect contact name. Data {data}",
                           client_sock)

    def del_contact(self, data: dict, client_sock: socket.SocketType):
        client_name = data[consts.USER][consts.ACCOUNT_NAME]
        contact_name = data.get(consts.CONTACT_NAME)
        if client_name != consts.GUEST and contact_name:
            self.db.remove_contact(client_name, contact_name)
            response = {
                consts.RESPONSE: 202,
                consts.TIME: time(),
                consts.ALERT: 'OK',
            }
            post_data(response, client_sock)
            return
        self.error_handler(consts.INVALID_USERNAME,
                           f"Client is Guest or contact name not found. Data {data}",
                           client_sock)

    @staticmethod
    def error_handler(error: str, log_string: str, client_sock: socket.SocketType):
        SERVER_LOGGER.error(log_string or error)
        response = {
            consts.RESPONSE: 400,
            consts.TIME: time(),
            consts.ERROR: error,
        }
        post_data(response, client_sock)


def extract_args() -> (str, int):
    argv = sys.argv[1:]
    SERVER_LOGGER.debug(f'Server app started with args: {argv}')
    parser = ArgumentParser()
    parser.add_argument('-a', '--ip', default=consts.DEFAULT_LISTEN_IP, nargs='?')
    parser.add_argument('-p', '--port', default=consts.DEFAULT_SERVER_PORT, type=int, nargs='?')
    args = parser.parse_args(argv)
    listen_ip = ip_address(args.ip)
    listen_port = args.port
    return listen_ip, listen_port


if __name__ == '__main__':
    server = Server()
    try:
        server.start(*extract_args())
    except Exception as e:
        SERVER_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
