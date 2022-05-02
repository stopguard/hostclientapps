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
            self.register_date = datetime.now()

    class Online:
        def __init__(self, user_id, ip, port):
            self.id = None
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.login_date = datetime.now()

    class History:
        def __init__(self, user_id, ip, port, action):
            self.id = None
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.action = action
            self.date_time = datetime.now()

    class Contacts:
        def __init__(self, user_id, contact_id):
            self.id = None
            self.user_id = user_id
            self.contact_id = contact_id
            self.add_date = datetime.now()

    def __init__(self, db_url):
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String(96)),
                            Column('register_date', DateTime))

        online_table = Table('Online', self.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('user_id', ForeignKey('Users.id')),
                             Column('ip', String),
                             Column('port', Integer),
                             Column('login_date', DateTime))

        history_table = Table('History', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('user_id', ForeignKey('Users.id')),
                              Column('ip', String),
                              Column('port', Integer),
                              Column('action', String(1)),
                              Column('date_time', DateTime))

        contacts_table = Table('Contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('user_id', ForeignKey('Users.id')),
                               Column('contact_id', ForeignKey('Users.id')),
                               Column('add_date', DateTime))

        self.metadata.create_all(self.db_engine)
        mapper(self.Users, users_table)
        mapper(self.Online, online_table)
        mapper(self.History, history_table)
        mapper(self.Contacts, contacts_table)

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

    def get_contacts(self, username):
        user = self.session.query(self.Users).filter_by(username=username).first()
        queryset = self.session.query(self.Users.username, self.Contacts).\
            filter(self.Contacts.user_id == user.id).\
            join(self.Contacts, self.Contacts.contact_id == self.Users.id)
        return [contact[0] for contact in queryset.all()]

    def add_contact(self, username, contact):
        user = self.session.query(self.Users).filter_by(username=username).first()
        contact = self.session.query(self.Users).filter_by(username=contact).first()
        if not contact:
            return
        exists = self.session.query(self.Contacts).filter_by(user_id=user.id, contact_id=contact.id).count()
        if not exists:
            new_contact = self.Contacts(user.id, contact.id)
            self.session.add(new_contact)
            self.session.commit()

    def remove_contact(self, username, contact):
        user = self.session.query(self.Users).filter_by(username=username).first()
        contact = self.session.query(self.Users).filter_by(username=contact).first()
        if not contact:
            return
        queryset = self.session.query(self.Contacts).filter_by(user_id=user.id, contact_id=contact.id).first()
        if queryset:
            self.session.delete(queryset)
            self.session.commit()


def print_db():
    print('======================================================='
          '\nALL')
    pprint(db.get_users())
    print('ONLINE')
    pprint(db.get_online())
    print('HISTORY test1')
    pprint(db.get_history(username='test1'))
    print('HISTORY ALL')
    pprint(db.get_history())
    print('CONTACTS test1')
    pprint(db.get_contacts('test1'))
    print('CONTACTS test2')
    pprint(db.get_contacts('test2'))


if __name__ == '__main__':
    print('INIT')
    db = Storage(MAIN_SERVER_DB)
    db.connect_user('test1', '192.168.0.2', '2222')
    db.connect_user('test2', '192.168.0.3', '3333')
    db.add_contact('test1', 'test2')
    db.add_contact('test2', 'test1')
    print_db()
    db.disconnect_user(ip='192.168.0.2', port='2222')
    db.remove_contact('test2', 'test1')
    print_db()
