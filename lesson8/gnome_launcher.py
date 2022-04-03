import os
import signal
import subprocess
import sys
import time

INTERPRETER_PATH = sys.executable
WORK_DIR = os.getcwd()


def kill_all(targets: list):
    """kill processes in targets list"""
    while targets:
        process = targets.pop()
        os.killpg(process.pid, signal.SIGINT)


def close_launcher(tasks: list, *args):
    """kill processes in tasks list and close launcher"""
    kill_all(tasks)
    exit(0)


def up_and_return_module(module_file, args=''):
    """up and return process with args string"""
    time.sleep(0.2)
    command_line = ' '.join((INTERPRETER_PATH, os.path.join(WORK_DIR, module_file), args))
    full_args = 'gnome-terminal', '--disable-factory', '--', 'bash', '-c', command_line
    return subprocess.Popen(full_args, preexec_fn=os.setpgrp)


def start_apps(current_tasks: list, senders=2, readers=2) -> list:
    """start or restart server and clients windows.
    can receive senders and readers counts in args"""
    kill_all(current_tasks)
    new_process_list = [up_and_return_module('server.py')]
    for _ in range(senders):
        new_process_list.append(up_and_return_module('client.py', '-m send'))
    for _ in range(readers):
        new_process_list.append(up_and_return_module('client.py'))
    return new_process_list


# callback dict. may be updated.
actions = {
    's': start_apps,
    'start': start_apps,
}

process_list = []
while True:
    choice = input('Введите:\ns или start - для запуска или перезапуска окон\nлюбой другой текст - для выхода\n>>> ')
    process_list = actions.get(choice, close_launcher)(process_list)
