import json
import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
import common.settings as consts
from common.utils import get_data, post_data
import modules.socket_emulator as socket


class TestClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # initial data
        cls.request = {
            consts.USER: {consts.ACCOUNT_NAME: 'Guest'},
            consts.ACTION: consts.PRESENCE,
            consts.TIME: 100.500,
        }
        cls.response = {
            consts.RESPONSE: 200,
            consts.ALERT: 'OK',
        }
        cls.wrong_data = 'rasras'
        cls.unserializable_data = {consts.RESPONSE, consts.ALERT}

    def test_get_data_request(self):
        sock = socket.socket(self.request)
        unpacked_data = get_data(sock)
        self.assertEqual(unpacked_data, self.request)

    def test_get_data_response(self):
        sock = socket.socket(self.response)
        unpacked_data = get_data(sock)
        self.assertEqual(unpacked_data, self.response)

    def test_get_data_fail(self):
        sock = socket.socket(self.wrong_data)
        unpacked_data = get_data(sock)
        self.assertEqual(unpacked_data, {})

    def test_post_data_sent_data_check(self):
        sock = socket.socket(self.response)
        post_data(self.request, sock)
        serialized_request = json.dumps(self.request).encode(consts.ENCODING)
        self.assertEqual(serialized_request, sock.received_data)

    def test_post_data_unserializable(self):
        sock = socket.socket(self.response)
        self.assertRaises(TypeError, post_data, self.unserializable_data, sock)
