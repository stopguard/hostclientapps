import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
import common.settings as consts
from client import presence, response_handler


class TestClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.username = 'Guest'
        cls.data_to_send = {
            consts.ACTION: consts.PRESENCE,
            consts.USER: {consts.ACCOUNT_NAME: 'Guest'},
            consts.TIME: 100.500,
        }
        cls.response_ok = {
            consts.RESPONSE: 200,
            consts.ALERT: 'OK',
        }
        cls.response_fail = {
            consts.RESPONSE: 400,
            consts.ERROR: 'Bad request',
        }
        cls.response_wrong_dict = {}
        cls.response_unknown_fail = {consts.RESPONSE: 123}

    def test_presence(self):
        presence_data = presence(self.username)
        presence_data[consts.TIME] = 100.500
        self.assertEqual(presence_data, self.data_to_send)

    def test_response_handler_ok(self):
        self.assertEqual(response_handler(self.response_ok), '200: OK')

    def test_response_handler_error(self):
        self.assertEqual(response_handler(self.response_fail), '400: Bad request')

    def test_response_handler_unknown_error(self):
        self.assertEqual(response_handler(self.response_unknown_fail), '123: unknown error')

    def test_response_handler_wrong_dict(self):
        self.assertEqual(response_handler(self.response_wrong_dict), 'Wrong data')

    def test_response_handler_wrong_data(self):
        self.assertRaises(AttributeError, response_handler, 'wrong data')
