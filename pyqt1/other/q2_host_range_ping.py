import ipaddress
import re
from pprint import pprint

from q1_host_ping import host_ping


def host_range_ping(start_address, count: int) -> (dict, dict):
    """
    Convert address range to address list and send to ping function
    Return ping checking results in two formats
    First dict have address keys with test result values
    Second dict have address lists with result keys
    """
    address_list = []
    current_address = start_address
    incr = 1 if count > 0 else -1
    for _ in range(0, incr * count):
        address_list.append(current_address)
        current_address += incr
    return host_ping(address_list)


def ping_init() -> (dict, dict):
    """
    Transparent function for input data for sending this to host_range_ping and return result.
    """
    print('Input addresses range')

    while True:
        typed_address = input('Input start address: ')
        try:
            start_addr = ipaddress.ip_address(typed_address)
            break
        except ValueError:
            print(f'This value ({typed_address}) is not IP address.')

    type_checker_re = re.compile(r'^[+-]?\d+$')
    last_octet = int(str(start_addr).split('.')[-1])
    while True:
        typed_range = input('Input steps count for address range: ')
        if type_checker_re.match(typed_range) is not None and 0 < (last_octet + int(typed_range)) < 255:
            checked_range = int(typed_range)
            break
        print('You print wrong data. Need integer number')

    return host_range_ping(start_addr, checked_range)


if __name__ == '__main__':
    checked, _ = ping_init()
    print('')
    pprint(checked)
