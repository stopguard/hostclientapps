"""
Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
    формирующий новый «отчетный» файл в формате CSV.

Создать функцию get_data(), в которой в цикле осуществляется:
    перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров:
    «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
    Значения каждого параметра поместить в соответствующий список.
В этой же функции создать главный список для хранения данных отчета main_data
    поместить в него названия столбцов отчета в виде списка.
Значения для этих столбцов также оформить в виде списка и поместить в файл main_data

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать:
    получение данных через вызов функции get_data(),
    сохранение подготовленных данных в соответствующий CSV-файл;
"""
import csv
import os
import re
from pprint import pprint

import chardet


def get_data(dir_name: str) -> list:
    """
    returns system data list from info files
    :param dir_name: path to info files
    :return: [headers_list, info_list1, info_list2,...]
    """
    # тут можно было реализовать поиск в целевой папке всех файлов по шаблону, но лень
    file_list = [
        'info_1.txt',
        'info_2.txt',
        'info_3.txt',
    ]
    header = ('Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы')
    REGEX_LIST = [re.compile(r'^' + key + r':\s*(.+?)\s+$', re.MULTILINE) for key in header]
    path_list = [os.path.join(dir_name, filename) for filename in file_list]
    os_lists = ([], [], [], [])
    for file_path in path_list:
        with open(file_path, 'rb') as f:
            data = f.read()
        code_table = chardet.detect(data).get('encoding', 'ascii')
        data = data.decode(code_table)
        for idx, regex in enumerate(REGEX_LIST):
            found = regex.findall(data)
            found = found[0] if found else 'nothing'
            os_lists[idx].append(found)
        # не совсем понятно нужно ли писать каждый полученный список в отдельный файл.
        # архитектурно этот функционал в "get_data()" выглядит странно, поэтому не решил, что не надо
        # добавлю, если потребуется
    writable_data = [header]
    for system in zip(*os_lists):
        writable_data.append(system)
    return writable_data


def write_to_csv(path: str):
    """
    write os data from info files to selected path
    :param path: path to new csv file
    :return: None
    """
    dir_name = os.path.split(path)[0]
    data = get_data(dir_name)
    with open(path, 'w', encoding='utf-8') as f:
        f_writer = csv.writer(f)
        f_writer.writerows(data)


if __name__ == '__main__':
    target_dir = 'q1_files'
    target_filename = 'main_data.csv'
    write_to_csv(os.path.join(os.getcwd(), target_dir, target_filename))
