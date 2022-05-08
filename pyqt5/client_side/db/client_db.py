import os
import sys
from pprint import pprint
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, and_, or_
from sqlalchemy.orm import mapper, sessionmaker

sys.path.append(os.path.join(os.getcwd(), '../..'))
from common.settings import MAIN_CLIENT_DB


class Storage:

    class Contacts:
        def __init__(self, contact_name):
            self.id = None
            self.username = contact_name
            self.last_update = datetime.now()

    class History:
        def __init__(self, sender_name, receiver_name, message):
            self.id = None
            self.sender = sender_name
            self.receiver = receiver_name
            self.message = message
            self.date_time = datetime.now()

    def __init__(self, db_url, username):
        self.username = username
        self.db_engine = create_engine(f'{db_url}{username}.db3',
                                       echo=False,
                                       pool_recycle=7200,
                                       connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        contacts_table = Table('Contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('username', String(96)),
                               Column('last_update', DateTime))

        history_table = Table('History', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('sender', String(96)),
                              Column('receiver', String(96)),
                              Column('message', String(1024)),
                              Column('date_time', DateTime))

        self.metadata.create_all(self.db_engine)
        mapper(self.Contacts, contacts_table)
        mapper(self.History, history_table)
        self.session = sessionmaker(bind=self.db_engine)()

    def refresh_contacts(self, contact_list):
        self.session.query(self.Contacts).delete()
        for name in contact_list:
            contact = self.Contacts(name)
            self.session.add(contact)
        self.session.commit()

    def add_contact(self, contact_name=None):
        if contact_name and not self.is_contact_exists(contact_name):
            contact = self.Contacts(contact_name)
            self.session.add(contact)
            self.session.commit()

    def remove_contact(self, contact_name=None):
        if not contact_name:
            return
        contact = self.session.query(self.Contacts).filter_by(username=contact_name).first()
        if contact:
            self.session.delete(contact)

    def get_contacts(self):
        queryset = self.session.query(self.Contacts.username)
        return [contact_name[0] for contact_name in queryset.all()]

    def is_contact_exists(self, contact_name):
        return self.session.query(self.Contacts).filter_by(username=contact_name).count() > 0

    def add_to_history(self, sender, receiver, message_text):
        message = self.History(sender, receiver, message_text)
        self.session.add(message)
        self.session.commit()

    def get_history(self, talker=None):
        queryset = self.session.query(self.History)
        if talker:
            queryset = queryset.filter(or_(and_(self.History.sender == talker, self.History.receiver == self.username),
                                       and_(self.History.sender == self.username, self.History.receiver == talker)))
        return [[message.sender, message.receiver, message.message, message.date_time] for message in queryset.all()]


if __name__ == '__main__':
    print('INIT')
    db = Storage(MAIN_CLIENT_DB, 'test')
    db.add_contact('test contact')
    print(db.get_contacts())
    test_contacts = [f'cont{i}' for i in range(5)]
    db.refresh_contacts(test_contacts)
    print(db.get_contacts())
    db.remove_contact('cont2')
    print(db.get_contacts())
    db.add_to_history('cont1', 'test', 'test text1')
    db.add_to_history('test', 'cont1', 'test text2')
    db.add_to_history('cont2', 'test', 'test text3')
    db.add_to_history('test', 'cont2', 'test text4')
    db.add_to_history('cont1', 'cont2', 'test text5')
    print('----------------')
    pprint(db.get_history())
    print('----------------')
    pprint(db.get_history('cont1'))
    print('----------------')
    pprint(db.get_history('cont2'))
