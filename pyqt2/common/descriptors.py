from ipaddress import IPv4Address, IPv6Address


class Port:
    def __set__(self, instance, value):
        if not 1024 < value < 65535:
            raise ValueError(f'Incorrect port number: {value}!')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class IP:
    def __set__(self, instance, value):
        val_class = type(value)
        if val_class != IPv4Address and val_class != IPv6Address:
            raise ValueError(f'Incorrect IP address: {value}!')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
