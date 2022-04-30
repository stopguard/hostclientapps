"""
Application variables
"""

# SERVER SIDE

DEFAULT_LISTEN_IP = '0.0.0.0'
SERVER_DB = 'sqlite:///common/server.db3'


# CLIENT SIDE

# Default server address
# Default value = '127.0.0.1'
DEFAULT_SERVER_IP = '127.0.0.1'


# OTHERS

# Encoding
# Default value = 'utf-8'
ENCODING = 'utf-8'

# Max request-response package length
# Default value = 640
MAX_PACKAGE_LENGTH = 640

# Default server port for clients connections
# Default value = 7777
DEFAULT_SERVER_PORT = 7777

# Keys
# Default values:
# ACCOUNT_NAME = 'username'
# ACTION = 'action'
# ALERT = 'alert'
# ALL = 'all'
# ERROR = 'error'
# MESSAGE = 'message'
# MESSAGE_TEXT = 'text'
# PRESENCE = 'presence'
# RECIPIENT = 'recipient'
# RESPONSE = 'response'
# SENDER = 'sender'
# TIME = 'time'
# USER = 'user'

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
ERROR = 'error'
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
