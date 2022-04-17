"""I not checked it, but must working"""

import subprocess
import sys
import time

INTERPRETER_PATH = sys.executable


def kill_all(targets: list):
    """kill processes in targets list"""
    while targets:
        process = targets.pop()
        process.kill()


def close_launcher(tasks: list, *args):
    """kill processes in tasks list and close launcher"""
    kill_all(tasks)
    exit(0)


def up_and_return_module(module_file, args=''):
    """up and return process with args string"""
    time.sleep(0.2)
    command_line = ' '.join((INTERPRETER_PATH, module_file, args))
    return subprocess.Popen(command_line, creationflags=subprocess.CREATE_NEW_CONSOLE)


def start_apps(current_tasks: list, clients) -> list:
    """start or restart server and clients windows.
    can receive clients count in args"""
    kill_all(current_tasks)
    new_process_list = [up_and_return_module('server.py')]
    for num in range(1, clients + 1):
        new_process_list.append(up_and_return_module('client.py', f'-n test{num}'))
    return new_process_list


# callback dict. may be updated.
actions = {
    's': start_apps,
    'start': start_apps,
}

process_list = []
while True:
    input_action = input(f'Введите:\n'
                         f'{"s или start":<20} - для запуска или перезапуска окон\n'
                         f'{"start 5":<20} - добавьте число к команде запуска для указания количества окон\n'
                         f'{"любой другой текст":<20} - для выхода\n>>> ')
    choices_list = input_action.split(' ')
    choice = choices_list[0]
    arg = int(choices_list[1]) if len(choices_list) > 1 and choices_list[1].isdigit() else 4
    process_list = actions.get(choice, close_launcher)(process_list, arg)
