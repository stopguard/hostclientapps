import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..', '..'))
import common.settings as consts


class SocketType:
    """socket actions imitation"""
    def __init__(self, initial_dict):
        self.__data = initial_dict
        self.received_data = None
        self.response_data = None

    def recv(self, buffersize):
        """receive incomming message imitation"""
        serialized_request = json.dumps(self.__data)
        return serialized_request.encode(consts.ENCODING)

    def send(self, sent_data):
        """send outgoing message imitation"""
        self.received_data = sent_data
        serialized_response = json.dumps(self.__data)
        self.response_data = serialized_response.encode(consts.ENCODING)


socket = SocketType
