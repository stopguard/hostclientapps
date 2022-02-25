import json
import socket

from .settings import MAX_PACKAGE_LENGTH, ENCODING


def get_msg(cl_sock: socket.SocketType) -> dict:
    """
    unpack received data
    :param cl_sock: target socket
    :return: received data dict
    """
    received_data = cl_sock.recv(MAX_PACKAGE_LENGTH)
    decoded_data = received_data.decode(ENCODING)
    deserialized_data = json.loads(decoded_data)
    if type(deserialized_data) == dict:
        return deserialized_data
    return {}


def post_msg(data: dict, sock: socket.SocketType):
    """
    serialize and send data to target socket
    :param data: data being sent
    :param sock: target socket
    """
    serialized_data = json.dumps(data)
    encoded_data = serialized_data.encode(ENCODING)
    sock.send(encoded_data)
