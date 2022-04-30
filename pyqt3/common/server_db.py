from sqlalchemy import MetaData, Table, Column, Integer, String

from .settings import SERVER_DB


class Storage:

    class Users:
        pass

    class ActiveUsers:
        pass

    class History:
        pass

    def __init__(self):
        pass

    def connect_user(self):
        pass

    def disconnect_user(self):
        pass

    def get_users(self):
        pass

    def get_online(self):
        pass

    def get_history(self):
        pass


if __name__ == '__main__':
    pass
