from dis import get_instructions


class ServerMaker(type):
    def __init__(cls, cls_name, bases, cls_dict):

        method_list = []
        attr_list = []

        for func in cls_dict:
            try:
                instructions = get_instructions(cls_dict[func])
            except TypeError:
                pass
            else:
                for op in instructions:
                    if op.opname == 'LOAD_GLOBAL' and op.argval not in method_list:
                        method_list.append(op.argval)
                    elif op.opname == 'LOAD_ATTR' and op.argval not in attr_list:
                        attr_list.append(op.argval)

        if 'connect' in method_list:
            raise TypeError('Unable usage [connect] method in [Server] class')
        if 'SOCK_STREAM' not in attr_list and 'AF_INET' not in attr_list:
            raise TypeError('Incorrect socket initialising')

        super().__init__(cls_name, bases, cls_dict)
