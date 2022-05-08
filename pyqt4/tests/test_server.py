import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
import common.settings as consts
from server import data_handler


class TestClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.received_presence = {
            consts.USER: {consts.ACCOUNT_NAME: 'Guest'},
            consts.ACTION: consts.PRESENCE,
            consts.TIME: 100.500,
        }
        cls.received_presence_with_wrong_username = {
            consts.USER: {consts.ACCOUNT_NAME: '39'},
            consts.ACTION: consts.PRESENCE,
            consts.TIME: 100.500,
        }
        cls.received_presence_with_wrong_action = {
            consts.USER: {consts.ACCOUNT_NAME: 'Guest'},
            consts.ACTION: '39',
            consts.TIME: 100.500,
        }
        cls.received_presence_without_user = {
            consts.ACTION: consts.PRESENCE,
            consts.TIME: 100.500,
        }
        cls.received_presence_without_time = {
            consts.USER: {consts.ACCOUNT_NAME: 'Guest'},
            consts.ACTION: consts.PRESENCE,
        }

        cls.response_ok = {
            consts.RESPONSE: 200,
            consts.TIME: 100.500,
            consts.ALERT: 'OK',
        }
        cls.response_fail = {
            consts.RESPONSE: 400,
            consts.TIME: 100.500,
            consts.ERROR: 'Bad request',
        }

    def test_response_ok(self):
        response_data = data_handler(self.received_presence)
        response_data[consts.TIME] = 100.500
        self.assertEqual(response_data, self.response_ok)

    def test_response_with_wrong_username(self):
        response_data = data_handler(self.received_presence_with_wrong_username)
        response_data[consts.TIME] = 100.500
        self.assertEqual(response_data, self.response_fail)

    def test_response_with_wrong_action(self):
        response_data = data_handler(self.received_presence_with_wrong_action)
        response_data[consts.TIME] = 100.500
        self.assertEqual(response_data, self.response_fail)

    def test_response_without_user(self):
        response_data = data_handler(self.received_presence_without_user)
        response_data[consts.TIME] = 100.500
        self.assertEqual(response_data, self.response_fail)

    def test_response_without_time(self):
        response_data = data_handler(self.received_presence_without_time)
        response_data[consts.TIME] = 100.500
        self.assertEqual(response_data, self.response_fail)

    def test_response_wrong_data(self):
        self.assertRaises(AttributeError, data_handler, 'wrong data')
