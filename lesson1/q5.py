"""
Выполнить пинг веб-ресурсов yandex.ru, youtube.com
преобразовать результаты из байтовового в строковый тип на кириллице.
"""
from platform import system
from subprocess import Popen, PIPE

import chardet


def ping_pong(target: str) -> list:
    """ping source and returns a list of result byte lines"""
    multiple_arg = '-n' if system().lower() == 'windows' else '-c'
    args = ['ping', multiple_arg, '4']
    responses = Popen([*args, target], stdout=PIPE)
    return list(responses.stdout)


def convert_to_str(bytes_data: list) -> str:
    """convert list of byte lines to string"""
    str_line = ''
    if bytes_data:
        code_table = chardet.detect(bytes_data[0]).get('encoding', 'ascii')
        print(f'detected encoding: {code_table}')
        for bytes_line in bytes_data:
            str_line += bytes_line.decode(code_table)
    return str_line


if __name__ == '__main__':
    sources = ['yandex.ru', 'youtube.com']
    result = ''
    for server in sources:
        data = ping_pong(server)
        result += f'{convert_to_str(data)}\n'
    print(result)
