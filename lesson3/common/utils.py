import json

from .settings import MAX_PACKAGE_LENGTH, ENCODING


def get_msg(cl_sock):
    recieved_data = cl_sock.recv(MAX_PACKAGE_LENGTH)
    decoded_data = recieved_data.decode(ENCODING)
    deserialized_data = json.loads(decoded_data)
    if type(deserialized_data) == dict:
        return deserialized_data
    return {}


def post_msg(msg_txt, sock):
    serialized_data = json.dumps(msg_txt)
    encoded_data = serialized_data.encode(ENCODING)
    sock.send(encoded_data)
