"""
Каждое из слов «разработка», «сокет», «декоратор»
    представить в строковом формате
    и проверить тип и содержание соответствующих переменных.
Затем с помощью онлайн-конвертера
    преобразовать строковые представления в формат Unicode
    и также проверить тип и содержимое переменных.
"""


def check_and_print(lst, with_len=False):
    """print type, value and length (if 'with_len' value is True) of the item"""
    for item in lst:
        result = f'type:   {type(item)}\n' \
                 f'value:  {item}'
        result += f'\nlength: {len(item)}' if with_len else ''
        print(result)


if __name__ == '__main__':
    str_words = ['разработка',
                 'сокет',
                 'декоратор']
    str_unicode_words = ['%u0440%u0430%u0437%u0440%u0430%u0431%u043E%u0442%u043A%u0430',
                         '%u0441%u043E%u043A%u0435%u0442',
                         '%u0434%u0435%u043A%u043E%u0440%u0430%u0442%u043E%u0440']
    byte_unicode_words = [b'%u0440%u0430%u0437%u0440%u0430%u0431%u043E%u0442%u043A%u0430',
                          b'%u0441%u043E%u043A%u0435%u0442',
                          b'%u0434%u0435%u043A%u043E%u0440%u0430%u0442%u043E%u0440']

    print('str_words types and values:')
    check_and_print(str_words)

    print('str_unicode_words types and values:')
    check_and_print(str_unicode_words)

    print('byte_unicode_words types and values:')
    check_and_print(byte_unicode_words)
