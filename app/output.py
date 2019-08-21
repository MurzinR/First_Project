import json
from enum import Enum
from functools import wraps
from uuid import UUID


def correct_output(func):
    """Приводит выходные данные к ожидаемому формату"""

    class MyEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, Enum):
                return o.name
            if isinstance(o, UUID):
                return str(o)
            return json.JSONEncoder.default(self, o)

    @wraps(func)
    def wrapper(*args, **kwargs):
        input_data = func(*args, **kwargs)
        size_input_data = len(input_data)
        if size_input_data == 1 or input_data[1] < 400:
            return json.dumps({'ok': True,
                               'data': input_data[0],
                               'message': input_data[2] if size_input_data == 3 else None},
                              cls=MyEncoder), input_data[1] if size_input_data > 1 else 200
        return json.dumps({'ok': False,
                           'issues': input_data[0],
                           'message': input_data[2] if size_input_data == 3 else None},
                          cls=MyEncoder), input_data[1] if size_input_data > 1 else 404

    return wrapper
