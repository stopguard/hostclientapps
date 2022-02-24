"""
Написать скрипт, автоматизирующий заполнение файла orders.json данными.

Создать функцию write_order_to_json(), в которую передается 5 параметров
    товар (item), количество (quantity), цена (price), покупатель (buyer), дата (date)
Функция должна предусматривать запись данных в виде словаря в файл orders.json
При записи данных указать величину отступа в 4 пробельных символа
"""
import os
import json


def write_order_to_json(item,
                        quantity,
                        price,
                        buyer,
                        date):
    """
    add order to orders file
    """
    order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    }
    target_dir = 'q2_files'
    target_filename = 'orders.json'
    orders_file_path = os.path.join(os.getcwd(), target_dir, target_filename)
    try:
        with open(orders_file_path, 'r', encoding='utf-8') as f:
            orders_data = json.load(f)
    except Exception as exc:
        orders_data = {'orders': []}
        print(f'Error: {exc}.\nCreate default value.')
    orders = orders_data.get('orders', []) if type(orders_data) == dict else []
    orders.append(order)
    orders_data = {'orders': orders}
    with open(orders_file_path, 'w', encoding='utf-8') as f:
        json.dump(orders_data, f, indent=4)


for i in range(1, 13):
    write_order_to_json(f'Товар{i}', i, i * 100, f'Клиент{i}', f'{i:0>2}.{i:0>2}.2022')
