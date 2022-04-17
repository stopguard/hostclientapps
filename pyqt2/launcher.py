import os
import signal
import subprocess
import sys
import time

from argparse import ArgumentParser


class Launcher:
    START = 'start'
    KILL_ALL = 'kill'
    EXIT = 'exit'
    ACTIONS = [START, KILL_ALL, EXIT]

    def __init__(self):
        self.__process_list = []
        self.__interpreter_path = sys.executable
        self.__work_dir = os.getcwd()
        if os.name == 'posix':
            self.up_module = self.__up_module_gnome
            self.kill_all = self.__kill_all_gnome
        elif os.name == 'nt':
            self.up_module = self.__up_module_win
            self.kill_all = self.__kill_all_win
        else:
            raise Exception('This OS is not supported')

    def run(self, action, *args):
        actions = {
            self.START: self.start_apps,
            self.KILL_ALL: self.kill_all,
            self.EXIT: self.close_launcher,
        }
        actions[action](*args)

    def __up_module_win(self, module_file, args=''):
        """up and return process with args string in windows"""
        time.sleep(0.2)
        command_line = ' '.join((self.__interpreter_path, os.path.join(self.__work_dir, module_file), args))
        process = subprocess.Popen(command_line, creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.__process_list.append(process)

    def __up_module_gnome(self, module_file, args=''):
        """up and return process with args string in linux with gnome ui"""
        time.sleep(0.2)
        command_line = ' '.join((self.__interpreter_path, os.path.join(self.__work_dir, module_file), args))
        full_args = 'gnome-terminal', '--disable-factory', '--', 'bash', '-c', command_line
        process = subprocess.Popen(full_args, preexec_fn=os.setpgrp)
        self.__process_list.append(process)

    def __kill_all_win(self, *args):
        """kill processes in targets list in windows"""
        print('Killing of running processes...')
        while self.__process_list:
            process = self.__process_list.pop()
            try:
                process.kill()
            except Exception:
                pass
        print('OK')

    def __kill_all_gnome(self, *args):
        """kill processes in targets list in linux with gnome ui"""
        print('Killing of running processes...')
        while self.__process_list:
            process = self.__process_list.pop()
            try:
                os.killpg(process.pid, signal.SIGINT)
            except Exception:
                pass
        print('OK')

    def start_apps(self, clients_count: int, *args):
        """start or restart server and clients windows.
        can receive clients count in args"""
        self.kill_all(self.__process_list)
        print('Running the server process')
        self.up_module('server.py')
        print('Running client processes')
        for num in range(1, clients_count + 1):
            self.up_module('client.py', f'-n test{num}')
        print('OK\n')

    def close_launcher(self, *args):
        """kill processes in tasks list and close launcher"""
        self.kill_all()
        print('Closing the launcher')
        exit(0)


def arg_parse(command_line: str) -> (str, int):
    command_line = command_line.strip()
    if not command_line:
        return '', 0
    parser = ArgumentParser()
    parser.add_argument('action', nargs='?')
    parser.add_argument('clients_count', default=4, type=int, nargs='?')
    argv = command_line.split(' ')
    args = parser.parse_args(argv)

    action = args.action if args.action in Launcher.ACTIONS else Launcher.EXIT
    clients_count = args.clients_count
    return action, clients_count


launcher = Launcher()

while True:
    input_action = input(f'Введите:\n'
                         f'{"start":<20} - для запуска или перезапуска окон\n'
                         f'{"start 5":<20} - добавьте число к команде запуска для указания количества окон\n'
                         f'{"kill":<20} - для закрытия всех окон\n'
                         f'{"любой другой текст":<20} - для выхода\n>>> ')
    choice, clients = arg_parse(input_action)
    if choice:
        launcher.run(choice, clients)

