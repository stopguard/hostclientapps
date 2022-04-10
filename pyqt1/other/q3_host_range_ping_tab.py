from tabulate import tabulate

from q2_host_range_ping import ping_init

if __name__ == '__main__':
    _, results = ping_init()
    print('')
    print(tabulate(results, headers='keys', tablefmt='pipe'))
