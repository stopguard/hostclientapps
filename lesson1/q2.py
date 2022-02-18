"""
Каждое из слов «class», «function», «method»
    записать в байтовом типе без преобразования в последовательность кодов (не используя методы encode и decode)
    и определить тип,
    содержимое
    и длину соответствующих переменных.
"""
from q1 import check_and_print


word_list = [b'class',
             b'function',
             b'method']

check_and_print(word_list, True)
