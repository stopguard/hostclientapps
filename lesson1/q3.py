"""
Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
Важно: решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем
"""


def bytes_compatible_check(word: str):
    """returns true if string can be converted to bytes"""
    for character in word:
        if ord(character) > 127:
            return False
    return True


words_for_check = ['attribute',
                   'класс',
                   'функция',
                   'type']

incompatible_words = []
for item in words_for_check:
    if not bytes_compatible_check(item):
        incompatible_words.append(item)

print(f'all words:\n'
      f'{words_for_check}\n'
      f'incompatible words:\n'
      f'{incompatible_words}')
