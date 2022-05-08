from dis import get_instructions


class ClientMaker(type):
    def __init__(cls, cls_name, bases, cls_dict):
        get_check = False
        post_check = False

        for func in cls_dict:
            try:
                instructions = get_instructions(cls_dict[func])
            except TypeError:
                pass
            else:
                for op in instructions:
                    if op.opname == 'LOAD_GLOBAL':
                        method_name = op.argval
                        if method_name in ('accept', 'listen'):
                            raise TypeError(f'Unable usage [{method_name}] method in [Client] class')
                        get_check = True if method_name == 'get_data' else get_check
                        post_check = True if method_name == 'post_data' else post_check

        func_check = get_check and post_check
        if not func_check:
            raise TypeError('Required function is missing')

        super().__init__(cls_name, bases, cls_dict)
