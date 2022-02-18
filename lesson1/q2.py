"""
Каждое из слов «class», «function», «method»
    записать в байтовом типе без преобразования в последовательность кодов (не используя методы encode и decode)
    и опintределить тип,
    содержимое
    и длину соответствующих переменных.
"""
from q1 import check_and_print


word_list = ['class',
             'function',
             'method']

word_list = map(lambda x: eval("b'" + f"{x}'"), word_list)

check_and_print(word_list, True)
