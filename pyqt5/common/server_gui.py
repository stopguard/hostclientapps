import os
import sys

from PyQt5 import QtWidgets, QtGui

sys.path.append(os.path.join(os.getcwd(), '..'))
import common.settings as consts


class ServerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_table = None

        self.setWindowTitle('Server GUI')
        self.setFixedSize(800, 600)

        self.active_users_button = QtWidgets.QAction('Active users', self)
        self.all_users_button = QtWidgets.QAction('All users', self)
        self.history_button = QtWidgets.QAction('History', self)
        self.config_button = QtWidgets.QAction('Edit config')
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.triggered.connect(QtWidgets.qApp.quit)

        self.toolbar = self.addToolBar('')
        self.toolbar.addAction(self.active_users_button)
        self.toolbar.addAction(self.all_users_button)
        self.toolbar.addAction(self.history_button)
        self.toolbar.addAction(self.config_button)
        self.toolbar.addAction(exit_action)

        self.hint_label = QtWidgets.QLabel('Active users', self)
        self.hint_label.move(10, 30)
        self.hint_label.setFixedSize(780, 20)

        self.main_table = QtWidgets.QTableView(self)
        self.main_table.move(10, 60)
        self.main_table.setFixedSize(780, 530)

        self.show()

    def show_active_users(self, db):
        self.current_table = self.show_active_users
        users_list = db.get_online()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['Username', 'IP', 'Port', 'Login date'])
        for username, ip, port, date in users_list:
            username = QtGui.QStandardItem(username)
            ip = QtGui.QStandardItem(ip)
            port = QtGui.QStandardItem(str(port))
            date = QtGui.QStandardItem(date.strftime('%d.%m.%y %H:%M:%S'))
            username.setEditable(False)
            ip.setEditable(False)
            port.setEditable(False)
            date.setEditable(False)
            arr.appendRow([username, ip, port, date])
        self.hint_label.setText('Active users')
        self.show_content(arr)

    def show_all_users(self, db):
        self.current_table = self.show_all_users
        users_list = db.get_users()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['id', 'Username', 'Msg sent', 'PM received', 'Last login', 'Register'])
        for user_id, username, sent, received, last_login, register_date in users_list:
            user_id = QtGui.QStandardItem(str(user_id))
            username = QtGui.QStandardItem(username)
            sent = QtGui.QStandardItem(str(sent))
            received = QtGui.QStandardItem(str(received))
            last_login = QtGui.QStandardItem(last_login.strftime('%d.%m.%y %H:%M:%S'))
            register_date = QtGui.QStandardItem(register_date.strftime('%d.%m.%y %H:%M:%S'))
            user_id.setEditable(False)
            username.setEditable(False)
            sent.setEditable(False)
            received.setEditable(False)
            last_login.setEditable(False)
            register_date.setEditable(False)
            arr.appendRow([user_id, username, sent, received, last_login, register_date])
        self.hint_label.setText('All users')
        self.show_content(arr)

    def show_history(self, db):
        self.current_table = self.show_history
        records_list = db.get_history()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['Username', 'IP', 'Port', 'Action', 'Login date'])
        for username, ip, port, action, date in records_list:
            username = QtGui.QStandardItem(username)
            ip = QtGui.QStandardItem(ip)
            port = QtGui.QStandardItem(str(port))
            action = QtGui.QStandardItem(consts.ACTIONS_DICT[action])
            date = QtGui.QStandardItem(date.strftime('%d.%m.%y %H:%M:%S'))
            username.setEditable(False)
            ip.setEditable(False)
            port.setEditable(False)
            action.setEditable(False)
            date.setEditable(False)
            arr.appendRow([username, ip, port, action, date])
        self.hint_label.setText('Users history')
        self.show_content(arr)

    def show_content(self, content):
        self.main_table.setModel(content)
        self.main_table.resizeColumnsToContents()
        self.main_table.resizeRowsToContents()


class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, config: dict):
        super().__init__()

        self.setWindowTitle('Edit config')
        self.setFixedSize(400, 245)

        self.db_path_label = QtWidgets.QLabel('Database path', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.adjustSize()

        self.db_path_text = QtWidgets.QLineEdit(self)
        self.db_path_text.move(10, 30)
        self.db_path_text.setFixedSize(290, 20)
        self.db_path_text.setReadOnly(True)

        self.db_path_button = QtWidgets.QPushButton('Path...', self)
        self.db_path_button.move(305, 30)
        self.db_path_button.setFixedSize(85, 20)
        self.db_path_button.clicked.connect(self.open_file_window)

        self.db_filename_label = QtWidgets.QLabel('Database filename', self)
        self.db_filename_label.move(10, 60)
        self.db_filename_label.adjustSize()

        self.db_filename_text = QtWidgets.QLineEdit(self)
        self.db_filename_text.move(10, 80)
        self.db_filename_text.setFixedSize(380, 20)

        self.listen_ip_label = QtWidgets.QLabel('Listen IP. May be empty for listen all IP', self)
        self.listen_ip_label.move(10, 140)
        self.listen_ip_label.adjustSize()

        self.port_label = QtWidgets.QLabel('Port', self)
        self.port_label.move(300, 140)
        self.port_label.adjustSize()

        self.listen_ip_text = QtWidgets.QLineEdit(self)
        self.listen_ip_text.move(10, 160)
        self.listen_ip_text.setFixedSize(285, 20)

        self.port_text = QtWidgets.QSpinBox(self)
        self.port_text.move(300, 160)
        self.port_text.setFixedSize(90, 20)
        self.port_text.setRange(1025, 65535)

        self.ok_button = QtWidgets.QPushButton('OK', self)
        self.ok_button.move(220, 210)

        self.cancel_button = QtWidgets.QPushButton('Cancel', self)
        self.cancel_button.move(310, 210)
        self.cancel_button.clicked.connect(self.close)

        self.set_widgets_values(config)

        self.show()

    def set_widgets_values(self, config: dict):
        db_path = config.get('dbPath', consts.SERVER_DB_PATH)
        db_filename = config.get('dbFilename', consts.SERVER_DB_FILE)
        listen_ip = config.get('listenIp', consts.DEFAULT_LISTEN_IP)
        port = config.get('port', consts.DEFAULT_SERVER_PORT)
        self.db_path_text.setText(db_path)
        self.db_filename_text.setText(db_filename)
        self.listen_ip_text.setText(listen_ip)
        self.port_text.setValue(port)

    def get_widgets_values(self):
        return {
            'dbPath': self.db_path_text.text(),
            'dbFilename': self.db_filename_text.text(),
            'listenIp': self.listen_ip_text.text(),
            'port': self.port_text.value(),
        }

    def open_file_window(self):
        file_dialog = QtWidgets.QFileDialog(self)
        path = file_dialog.getExistingDirectory().replace('/', '\\')
        self.db_path_text.setText(path)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = ServerWindow()
    conf = ConfigWindow({})
    app.exec_()
