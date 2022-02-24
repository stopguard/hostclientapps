"""
Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата

Подготовить данные для записи в виде словаря
    первому ключу соответствует список, второму — целое число, третьему — вложенный словарь,
    где значение каждого ключа — это целое число с юникод-символом, отсутствующим в кодировке ASCII
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом:
    обеспечить стилизацию файла с помощью параметра default_flow_style
    установить возможность работы с юникодом: allow_unicode = True
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""
import os
from pprint import pprint

import yaml


# prepare data
writable_data = {
    'list': [1, 2, 'asd'],
    'number': 100500,
    'no_ascii_values_dict': {1: '1Б', 2: '2Г', 3: '3Д'},
}

# prepare file path
target_dir = 'q3_files'
target_filename = 'data.yaml'
target_file_path = os.path.join(os.getcwd(), target_dir, target_filename)

# serialize to yaml
with open(target_file_path, 'w', encoding='utf-8') as f:
    yaml.dump(writable_data, f, default_flow_style=False, allow_unicode=True)

print('writable data:')
pprint(writable_data)

# read raw data
with open(target_file_path, 'r', encoding='utf-8') as f:
    print(f'{"-" * 100}\nraw yaml data:\n{f.read()}')

# read deserialized data
with open(target_file_path, 'r', encoding='utf-8') as f:
    print(f'{"-" * 100}\ndeserialized yaml data:')
    pprint(yaml.load(f, Loader=yaml.FullLoader))

