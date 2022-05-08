from os.path import join
"""
Application variables
"""

# SERVER SIDE

# Default values:
# DEFAULT_LISTEN_IP = '0.0.0.0'
# MAIN_SERVER_DB = 'server.db3'
# SERVER_DB_PATH = join('server_side', 'db')
# SERVER_DB_FILE = 'server.db3'
# SERVER_DB = join(SERVER_DB_PATH, SERVER_DB_FILE)
# CONFIG_FILE = join('server_side', 'server_config.json')
DEFAULT_LISTEN_IP = '0.0.0.0'
MAIN_SERVER_DB = 'server.db3'
SERVER_DB_PATH = join('server_side', 'db')
SERVER_DB_FILE = 'server.db3'
SERVER_DB = join(SERVER_DB_PATH, SERVER_DB_FILE)
CONFIG_FILE = join('server_side', 'server_config.json')

# CLIENT SIDE

# Default values:
# DEFAULT_SERVER_IP = '127.0.0.1'
# MAIN_CLIENT_DB = f'sqlite:///{join("db", "client_")}'
# CLIENT_DB = f'sqlite:///{join("client_side", "db", "client_")}'
DEFAULT_SERVER_IP = '127.0.0.1'
MAIN_CLIENT_DB = f'sqlite:///{join("databases", "client_")}'
CLIENT_DB = f'sqlite:///{join("client_side", "db", "databases", "client_")}'

# OTHERS

# Default values:
# ENCODING = 'utf-8'
ENCODING = 'utf-8'

# Default values:
# MAX_PACKAGE_LENGTH = 640
MAX_PACKAGE_LENGTH = 640

# Default values:
# DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_PORT = 7777

# Keys
# Default values:
# ACCOUNT_NAME = 'username'
# ACTION = 'action'
# ALERT = 'alert'
# ALL = 'all'
# BAD_REQUEST = 'Bad request'
# CONNECT = 'Connect'
# CONNECT_KEY = 'C'
# DISCONNECT = 'Disconnect'
# DISCONNECT_KEY = 'D'
# ERROR = 'error'
# CONTACTS_ADD = 'add_contact'
# CONTACTS_ADD_KEY = '/add_contact'
# CONTACTS_DEL = 'del_contact'
# CONTACTS_DEL_KEY = '/del_contact'
# CONTACTS_GET = 'get_contacts'
# GUEST = 'Guest'
# HELP_KEYS = ['/h', '/help']
# REFRESH_CONTACTS_KEYS = ['/refresh_contacts', '/rc']
# GET_CONTACTS_KEYS = ['/contacts', '/c']
# INVALID_RECIPIENT = 'Recipient is not found'
# INVALID_SENDER = 'Invalid sender'
# INVALID_USERNAME = 'Invalid username'
# MESSAGE = 'message'
# MESSAGE_TEXT = 'text'
# OK = 'OK'
# PRESENCE = 'presence'
# PRIVATE_DELIMITER = '/p/'
# RECIPIENT = 'recipient'
# RESPONSE = 'response'
# SENDER = 'sender'
# SERVER = 'SERVER'
# CONTACT_NAME = 'contact name'
# TIME = 'time'
# USER = 'user'
# YOU = 'you'
# CLIENT_HELP = '\nHELP INFO\n' \
#               'Send every nonempty message for all readers\n' \
#               f'For private message send "<username>{PRIVATE_DELIMITER}<message>"\n' \
#               'examples:\n' \
#               f'  user1{PRIVATE_DELIMITER}hello world\n' \
#               f'  user1 {PRIVATE_DELIMITER} hello world\n' \
#               '  send "hello world" to "user1"\n\n' \
#               'Commands for load contact list from the server:\n' \
#               f'  {REFRESH_CONTACTS_KEYS}\n' \
#               f'example:\n' \
#               f'  {REFRESH_CONTACTS_KEYS[0]}\n\n' \
#               f'Commands for print your contacts:\n' \
#               f'  {GET_CONTACTS_KEYS}\n' \
#               f'example:\n' \
#               f'  {GET_CONTACTS_KEYS[0]}\n\n' \
#               f'For add user to contact list send "{CONTACTS_ADD_KEY} <username>"\n' \
#               f'example:\n' \
#               f'  {CONTACTS_ADD_KEY} user1\n\n' \
#               f'For remove user from contact list send "{CONTACTS_DEL_KEY} <username>"\n' \
#               f'example:\n' \
#               f'  {CONTACTS_DEL_KEY} user1'

ACCOUNT_NAME = 'username'
ACTION = 'action'
ALERT = 'alert'
ALL = 'all'
BAD_REQUEST = 'Bad request'
CONNECT = 'Connect'
CONNECT_KEY = 'C'
DISCONNECT = 'Disconnect'
DISCONNECT_KEY = 'D'
ERROR = 'error'
CONTACTS_ADD = 'add_contact'
CONTACTS_ADD_KEY = '/add_contact'
CONTACTS_DEL = 'del_contact'
CONTACTS_DEL_KEY = '/del_contact'
CONTACTS_GET = 'get_contacts'
GUEST = 'Guest'
HELP_KEYS = ['/h', '/help']
REFRESH_CONTACTS_KEYS = ['/refresh_contacts', '/rc']
GET_CONTACTS_KEYS = ['/contacts', '/c']
INVALID_RECIPIENT = 'Recipient is not found'
INVALID_SENDER = 'Invalid sender'
INVALID_USERNAME = 'Invalid username'
MESSAGE = 'message'
MESSAGE_TEXT = 'text'
OK = 'OK'
PRESENCE = 'presence'
PRIVATE_DELIMITER = '/p/'
RECIPIENT = 'recipient'
RESPONSE = 'response'
SENDER = 'sender'
SERVER = 'SERVER'
CONTACT_NAME = 'contact name'
TIME = 'time'
USER = 'user'
YOU = 'you'
CLIENT_HELP = '\nHELP INFO\n' \
              'Send every nonempty message for all readers\n' \
              f'For private message send "<username>{PRIVATE_DELIMITER}<message>"\n' \
              'examples:\n' \
              f'  user1{PRIVATE_DELIMITER}hello world\n' \
              f'  user1 {PRIVATE_DELIMITER} hello world\n' \
              '  send "hello world" to "user1"\n\n' \
              'Commands for load contact list from the server:\n' \
              f'  {REFRESH_CONTACTS_KEYS}\n' \
              f'example:\n' \
              f'  {REFRESH_CONTACTS_KEYS[0]}\n\n' \
              f'Commands for print your contacts:\n' \
              f'  {GET_CONTACTS_KEYS}\n' \
              f'example:\n' \
              f'  {GET_CONTACTS_KEYS[0]}\n\n' \
              f'For add user to contact list send "{CONTACTS_ADD_KEY} <username>"\n' \
              f'example:\n' \
              f'  {CONTACTS_ADD_KEY} user1\n\n' \
              f'For remove user from contact list send "{CONTACTS_DEL_KEY} <username>"\n' \
              f'example:\n' \
              f'  {CONTACTS_DEL_KEY} user1'

# Key dicts
ACTIONS_DICT = {
    CONNECT_KEY: CONNECT,
    DISCONNECT_KEY: DISCONNECT,
    CONTACTS_ADD_KEY: CONTACTS_ADD,
    CONTACTS_DEL_KEY: CONTACTS_DEL
}
