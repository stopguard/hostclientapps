"""
Выполнить пинг веб-ресурсов yandex.ru, youtube.com
преобразовать результаты из байтовового в строковый тип на кириллице.
"""
from platform import system
from subprocess import Popen, PIPE

import chardet


def ping_pong(sources: list, ping_count: str):
    multiple_arg = '-n' if system().lower() == 'windows' else '-c'
    args = ['ping', multiple_arg, ping_count]
    for target in sources:
        result = Popen([*args, target], stdout=PIPE)
        for line in result:
            result = chardet.detect(line)
            pass




sources = ['yandex.ru', 'youtube.com']
