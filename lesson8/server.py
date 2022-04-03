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


def data_handler(data: dict) -> (dict, str, str):
    """
    handle received data
    :param data: received data
    :returns: data to send, data type, recipient
    """
    error = consts.BAD_REQUEST
    try:
        error = data.get(consts.ERROR) or error
    except AttributeError as err:
        SERVER_LOGGER.error(f'Received data is not dict: {data}\n({err})')
    else:
        action = data.get(consts.ACTION)
        time_str = data.get(consts.TIME)
        account_name = data.get(consts.USER, {}).get(consts.ACCOUNT_NAME)
        recipient = consts.ALL if account_name == consts.GUEST else data.get(consts.RECIPIENT, consts.ALL)
        message_text = data.get(consts.MESSAGE_TEXT)
        is_basic_checked = time_str and account_name
        if action == consts.PRESENCE and is_basic_checked:
            SERVER_LOGGER.info(f"Correct [{action}] from [{account_name}] received")
            result = {
                consts.RESPONSE: 200,
                consts.TIME: time(),
                consts.ALERT: 'OK',
            }
            return result, consts.PRESENCE, account_name
        elif action == consts.MESSAGE and is_basic_checked and message_text:
            result = {
                consts.ACTION: consts.MESSAGE,
                consts.TIME: time(),
                consts.SENDER: account_name,
                consts.RECIPIENT: recipient,
                consts.MESSAGE_TEXT: message_text,
            }
            return result, consts.MESSAGE, recipient
        SERVER_LOGGER.warning(f'Incorrect request received: {data}')
    result = {
        consts.RESPONSE: 400,
        consts.TIME: time(),
        consts.ERROR: error,
    }
    return result, consts.RESPONSE, ''


def extract_args():
    argv = sys.argv[1:]
    SERVER_LOGGER.debug(f'Server app started with args: {argv}')
    parser = ArgumentParser()
    parser.add_argument('-a', '--ip', default=consts.DEFAULT_LISTEN_IP, nargs='?')
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
        authorised_socks = {}
        guest_socks = []
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
                        processed_data, data_type, target_name = data_handler(client_data)
                        if data_type == consts.PRESENCE:
                            if target_name == consts.GUEST:
                                guest_socks.append(client_sock)
                            elif target_name != consts.ALL and target_name not in authorised_socks:
                                authorised_socks[target_name] = client_sock
                            else:
                                processed_data, _, _ = data_handler({consts.ERROR: consts.INVALID_USERNAME})
                                post_data(processed_data, client_sock)
                                raise Exception(consts.INVALID_USERNAME)
                            post_data(processed_data, client_sock)
                            continue
                        if data_type == consts.MESSAGE:
                            sender_name = processed_data.get(consts.SENDER)
                            sender_sock = authorised_socks.get(sender_name)
                            target_sock = authorised_socks.get(target_name)
                            is_sender_authorised = sender_sock == client_sock
                            is_sender_guest = sender_name == consts.GUEST and client_sock in guest_socks
                            SERVER_LOGGER.debug(f'msg attrs: {sender_name=}, {sender_sock=}, {target_sock=}, '
                                                f'{is_sender_authorised=}, {is_sender_guest}')
                            if not is_sender_authorised and not is_sender_guest:
                                SERVER_LOGGER.error(f'sender {sender_name} is not authorised')
                                processed_data, _, _ = data_handler({consts.ERROR: consts.INVALID_SENDER})
                                post_data(processed_data, client_sock)
                                raise Exception(consts.INVALID_SENDER)
                            elif is_sender_authorised and target_sock:
                                SERVER_LOGGER.info(f'sender {sender_name} send private msg to {target_name}')
                                try:
                                    if target_sock not in listeners_list:
                                        raise Exception('Lost connection to client')
                                    post_data(processed_data, target_sock)
                                    if sender_name != target_name:
                                        post_data(processed_data, client_sock)
                                    continue
                                except Exception as err:
                                    SERVER_LOGGER.warning(f'Lost connection to {target_sock.getpeername()}. '
                                                          f'Connection dropped. Exception: {err}')
                                    target_sock.close()
                                    client_socks.remove(target_sock)
                                    del authorised_socks[target_name]
                            elif target_name == consts.ALL:
                                data_to_send.append(processed_data)
                                continue
                            processed_data, _, _ = data_handler({
                                consts.ACTION: consts.MESSAGE,
                                consts.TIME: time(),
                                consts.USER: {consts.ACCOUNT_NAME: consts.SERVER},
                                consts.RECIPIENT: sender_name,
                                consts.MESSAGE_TEXT: f'{consts.INVALID_RECIPIENT} ({target_name})',
                            })
                            post_data(processed_data, client_sock)
                            continue
                    except Exception as err:
                        SERVER_LOGGER.warning(f'Wrong data from client {client_sock.getpeername()}. '
                                              f'Connection dropped. Exception: {err}')
                        client_sock.close()
                        client_socks.remove(client_sock)

            if data_to_send and listeners_list:
                current_data = data_to_send[0]
                for current_listener in listeners_list:
                    try:
                        post_data(current_data, current_listener)
                    except Exception as err:
                        SERVER_LOGGER.warning(f'Client {current_listener.getpeername()} disconnected from the server. '
                                              f'Connection dropped. Exception: {err}')
                        if current_listener in guest_socks:
                            guest_socks.remove(current_listener)
                        else:
                            listener_key = False
                            for key, value in authorised_socks.items():
                                if value == current_listener:
                                    listener_key = key
                                    break
                            if listener_key:
                                del authorised_socks[listener_key]
                        client_socks.remove(current_listener)
                        current_listener.close()
                del data_to_send[0]


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        SERVER_LOGGER.critical(f'Unknown critical error: {e}')
        exit(1)
