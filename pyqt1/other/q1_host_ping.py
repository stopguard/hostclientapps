from pprint import pprint

import chardet
import ipaddress
import os
import re
import subprocess


def nix_ping(address) -> str:
    """Return check result for a connection to address for *nix systems"""
    ping = subprocess.run(f'ping {address} -c 1 -W 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    bytes_result = ping.stdout
    code_table = chardet.detect(bytes_result)['encoding']
    str_result = bytes_result.decode(code_table)
    reg_exp = re.compile(r'^.+?(\d+\.\d+/){3}.+$', re.MULTILINE)
    result = reg_exp.findall(str_result)
    if len(result) > 0:
        return 'Reachable'
    return 'Unreachable'


def win_ping(address) -> str:
    """Return check result for a connection to address for Windows systems"""
    ping = subprocess.run(f'ping {address} -n 1 -w 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    bytes_result = ping.stdout
    code_table = chardet.detect(bytes_result)['encoding']
    str_result = bytes_result.decode(code_table)
    reg_exp = re.compile(r'^.+?=(\d+)\S{2}.+$', re.MULTILINE)
    result = reg_exp.findall(str_result)
    if len(result) > 0:
        return 'Reachable'
    return 'Unreachable'


def host_ping(host_list) -> (dict, dict):
    """
    Return ping checking results for host list in two formats
    First dict have address keys with test result values
    Second dict have address lists with result keys
    """
    ping_func = OS_FUNCTIONS[OS_TYPE]['ping']
    addresses = {}
    results = {'Reachable': [], 'Unreachable': []}
    for addr in host_list:
        reachable = ping_func(addr)
        addresses[addr] = reachable
        results[reachable].append(addr)
    return addresses, results


OS_TYPE = os.name
OS_FUNCTIONS = {
    'nt': {'ping': win_ping},
    'posix': {'ping': nix_ping},
}

if __name__ == '__main__':
    print('Input all checkable addresses')
    check_list = []
    i = 1
    while True:
        typed_address = input(f'Address {i:0>2} (send "e" for go to hosts ping): ')
        if typed_address == 'e':
            break
        try:
            new_addr = ipaddress.ip_address(typed_address)
        except ValueError:
            selection = input(f'This value ({typed_address}) is not IP address.\n'
                              f'Save this in check list? ("yes" for accept) >>> ')
            if selection != 'yes':
                continue
            new_addr = typed_address
        check_list.append(new_addr)
        i += 1

    checked, _ = host_ping(check_list)
    print('')
    pprint(checked)
