"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard»
    из строкового представления в байтовое
    выполнить обратное преобразование (используя методы encode и decode).
"""
words = [
    'разработка',
    'администрирование',
    'protocol',
    'standard',
]

result = f'base words:\n' \
         f'{words}\n'

words = [item.encode('utf-8') for item in words]
result += f'\nconverted to bytes:' \
          f'\n{words}'

words = [item.decode('utf-8') for item in words]
result += f'\nconverted bytes to strings back' \
          f'\n{words}'

print(result)
