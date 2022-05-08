import json
import logging
import os.path
import socket
import sys
import threading
from argparse import ArgumentParser
from ipaddress import ip_address
from select import select
from time import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

import common.settings as consts
import server_side.log.server_log_config
from common.utils import get_data, post_data
from server_side.descriptors import IP, Port
from server_side.metaclasses import ServerMaker
from server_side.db.server_db import Storage
from server_side.gui.server_gui import ServerWindow, ConfigWindow

# server logger init
SERVER_LOGGER = logging.getLogger('server')


class Server(threading.Thread, metaclass=ServerMaker):
    listen_ip = IP()
    port = Port()

    def __init__(self, listen_ip, port: int, db_path):
        SERVER_LOGGER.debug(f'Initiating listen address: {listen_ip}:{port}.')

        self.listen_ip = listen_ip
        self.port = port

        self.client_socks = []
        self.authorised_socks = {}
        self.guest_socks = []
        self.listeners_list = []
        self.data_to_send = []
        self.socket = None
        self.db = Storage(db_path)
        self.actions = {
            consts.PRESENCE: self.presence,
            consts.MESSAGE: self.message,
            consts.CONTACTS_GET: self.get_contacts,
            consts.CONTACTS_ADD: self.add_contact,
            consts.CONTACTS_DEL: self.del_contact,
        }
        super().__init__()

    def run(self):

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
                    self.db.register_message(sender_name, recipient_name)
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
                self.db.register_message(sender_name, recipient_name)
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
                consts.ALERT: json.dumps(contacts),
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
    config_argv = {}
    try:
        with open(consts.CONFIG_FILE, 'r', encoding='utf-8') as config_file:
            config_argv = json.load(config_file)
    except Exception:
        pass
    commandline_argv = sys.argv[1:]
    SERVER_LOGGER.debug(f'Server app started with args: {commandline_argv}')
    parser = ArgumentParser()
    parser.add_argument('-a', '--ip', default='', nargs='?')
    parser.add_argument('-p', '--port', default=0, type=int, nargs='?')
    commandline_args = parser.parse_args(commandline_argv)
    db_path = config_argv.get('dbPath')
    if db_path and (not os.path.exists(db_path) or not os.path.isdir(db_path)):
        db_path = None
    db_filename = config_argv.get('dbFilename')
    full_db_path = os.path.join(db_path, db_filename) if db_path is not None and db_filename else consts.SERVER_DB
    listen_ip = commandline_args.ip or config_argv.get('listenIp') or consts.DEFAULT_LISTEN_IP
    listen_port = commandline_args.port or config_argv.get('port') or consts.DEFAULT_SERVER_PORT
    return ip_address(listen_ip), listen_port, full_db_path, config_argv


def main():
    def update_current_table():
        main_window.current_table(server.db)

    def edit_config():
        config_window = ConfigWindow(config)
        config_window.ok_button.clicked.connect(lambda _: save_config(config_window))

    def save_config(config_window):
        new_config = config_window.get_widgets_values()
        try:
            ip_address(new_config['listenIp'])
        except ValueError as err:
            msgbox = QMessageBox()
            msgbox.warning(config_window, 'Invalid IP address', str(err))
        else:
            with open(consts.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_config, f)
            config_window.close()

    ip, port, db, config = extract_args()
    server = Server(ip, port, db)
    server.daemon = True
    server.start()

    gui = QApplication(sys.argv)
    main_window = ServerWindow()

    main_window.show_active_users(server.db)

    timer = QTimer()
    timer.timeout.connect(update_current_table)
    timer.start(1000)

    main_window.active_users_button.triggered.connect(lambda _: main_window.show_active_users(server.db))
    main_window.all_users_button.triggered.connect(lambda _: main_window.show_all_users(server.db))
    main_window.history_button.triggered.connect(lambda _: main_window.show_history(server.db))
    main_window.config_button.triggered.connect(edit_config)

    gui.exec_()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        SERVER_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
