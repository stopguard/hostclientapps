"""
Создать текстовый файл test_file.txt, заполнить его тремя строками:
    «сетевое программирование», «сокет», «декоратор».
Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.
"""
from random import choice

from q5 import convert_to_str


code_tables = ['855', '866', 'cp1251', 'iso8859_5', 'koi8_r', 'utf-8']
path = 'test_file.txt'
data = ['сетевое программирование',
        'сокет',
        'декоратор']

# create file with random encoding
encoding = choice(code_tables)
print(f'choised encoding:  {encoding}')
with open(path, 'w', encoding=encoding) as f:
    writable_data = (f'{word}\n' for word in data)
    f.writelines(writable_data)

# read file
with open(path, 'rb') as f:
    file_data = f.readlines()

# decode file data
print(convert_to_str(file_data))
