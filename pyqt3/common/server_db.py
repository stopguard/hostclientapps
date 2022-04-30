import os
import sys
from pprint import pprint
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import mapper, sessionmaker

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.settings import MAIN_SERVER_DB, CONNECT_KEY, DISCONNECT_KEY


class Storage:

    class Users:
        def __init__(self, username):
            self.id = None
            self.username = username

    class Online:
        def __init__(self, user_id, ip, port):
            self.id = None
            self.user_id = user_id
            self.ip = ip
            self.port = port

    class History:
        def __init__(self, user_id, ip, port, action):
            self.id = None
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.action = action
            self.date_time = datetime.now()

    def __init__(self, db_url):
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String(96)))

        online_table = Table('Online', self.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('user_id', ForeignKey('Users.id')),
                             Column('ip', String),
                             Column('port', Integer))

        history_table = Table('History', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('user_id', ForeignKey('Users.id')),
                              Column('ip', String),
                              Column('port', Integer),
                              Column('action', String(1)),
                              Column('date_time', DateTime))

        self.metadata.create_all(self.db_engine)
        mapper(self.Users, users_table)
        mapper(self.Online, online_table)
        mapper(self.History, history_table)

        self.session = sessionmaker(bind=self.db_engine)()
        self.session.query(self.Online).delete()
        self.session.commit()

    def connect_user(self, username, ip, port):
        queryset = self.session.query(self.Users).filter_by(username=username)
        if queryset.count():
            user = queryset.first()
        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()

        user_session = self.Online(user.id, ip, port)
        self.session.add(user_session)
        self.session.add(self.History(user.id, ip, port, CONNECT_KEY))
        self.session.commit()
        return user_session.id

    def disconnect_user(self, **kwargs):
        user_session = self.session.query(self.Online).filter_by(**kwargs).first()
        if user_session:
            self.session.add(self.History(user_session.user_id, user_session.ip, user_session.port, DISCONNECT_KEY))
            self.session.delete(user_session)
            self.session.commit()
            print(f'Session {kwargs} dropped')
        else:
            print(f'Session {kwargs} not found')

    def get_users(self):
        queryset = self.session.query(self.Users.id,
                                      self.Users.username,
                                      func.max(self.History.date_time)).join(self.Users)\
            .filter(self.History.action == CONNECT_KEY)\
            .group_by(self.Users.id)
        return queryset.all()

    def get_online(self):
        queryset = self.session.query(self.Users.username,
                                      self.Online.ip,
                                      self.Online.port).join(self.Users)
        return queryset.all()

    def get_history(self, username=None, **kwargs):
        queryset = self.session.query(self.Users.username,
                                      self.History.ip,
                                      self.History.port,
                                      self.History.action,
                                      self.History.date_time).join(self.History)
        if username:
            queryset = queryset.filter(self.Users.username == username)
        if kwargs:
            queryset = queryset.filter_by(**kwargs)
        return queryset.all()


if __name__ == '__main__':
    print('\nINIT\n')
    db = Storage(MAIN_SERVER_DB)
    db.connect_user('test1', '192.168.0.2', '2222')
    db.connect_user('test2', '192.168.0.3', '3333')
    print('ALL')
    pprint(db.get_users())
    print('\nONLINE')
    pprint(db.get_online())
    db.disconnect_user(ip='192.168.0.2', port='2222')
    print('\nALL')
    pprint(db.get_users())
    print('\nONLINE')
    pprint(db.get_online())
    print('\nHISTORY')
    pprint(db.get_history(username='test1'))

