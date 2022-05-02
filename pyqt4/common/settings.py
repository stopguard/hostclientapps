"""
Application variables
"""

# SERVER SIDE

# Default values:
# DEFAULT_LISTEN_IP = '0.0.0.0'
# MAIN_SERVER_DB = 'sqlite:///server.db3'
# SERVER_DB = 'sqlite:///common/server.db3'
DEFAULT_LISTEN_IP = '0.0.0.0'
MAIN_SERVER_DB = 'sqlite:///server.db3'
SERVER_DB = 'sqlite:///common/server.db3'

# CLIENT SIDE

# Default values:
# DEFAULT_SERVER_IP = '127.0.0.1'
DEFAULT_SERVER_IP = '127.0.0.1'


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
# DISCONNECT = 'disconnect'
# CLIENT_HELP = '\nHELP INFO\n' \
#               'send every nonempty message for all readers\n' \
#               'for private message send "<username>/p/<message>"\n' \
#               'examples:\n' \
#               'user1/p/hello world\n' \
#               'user1 /p/ hello world\n' \
#               'send "hello world" to "user1"'
# CONNECT = 'connect'
# ERROR = 'error'
# GUEST = 'Guest'
# INVALID_RECIPIENT = 'Recipient is offline'
# INVALID_SENDER = 'Invalid sender'
# INVALID_USERNAME = 'Invalid username'
# MESSAGE = 'message'
# MESSAGE_TEXT = 'text'
# OK = 'OK'
# PRESENCE = 'presence'
# RECIPIENT = 'recipient'
# RESPONSE = 'response'
# SENDER = 'sender'
# SERVER = 'SERVER'
# TIME = 'time'
# USER = 'user'
# YOU = 'you'

ACCOUNT_NAME = 'username'
ACTION = 'action'
ALERT = 'alert'
ALL = 'all'
BAD_REQUEST = 'Bad request'
CLIENT_HELP = '\nHELP INFO\n' \
              'send every nonempty message for all readers\n' \
              'for private message send "<username>/p/<message>"\n' \
              'examples:\n' \
              'user1/p/hello world\n' \
              'user1 /p/ hello world\n' \
              'send "hello world" to "user1"'
CONNECT = 'Connect'
CONNECT_KEY = 'C'
DISCONNECT = 'Disconnect'
DISCONNECT_KEY = 'D'
ERROR = 'error'
CONTACTS_ADD = 'add_contacts'
CONTACTS_DEL = 'del_contacts'
CONTACTS_GET = 'get_contacts'
GUEST = 'Guest'
INVALID_RECIPIENT = 'Recipient is offline'
INVALID_SENDER = 'Invalid sender'
INVALID_USERNAME = 'Invalid username'
MESSAGE = 'message'
MESSAGE_TEXT = 'text'
OK = 'OK'
PRESENCE = 'presence'
RECIPIENT = 'recipient'
RESPONSE = 'response'
SENDER = 'sender'
SERVER = 'SERVER'
TIME = 'time'
USER = 'user'
YOU = 'you'

# Key dicts
ACTIONS_DICT = {CONNECT_KEY: CONNECT,
                DISCONNECT_KEY: DISCONNECT}
