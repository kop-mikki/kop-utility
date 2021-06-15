import re

def camel_to_snake(name):
    """changes a string from camelCase format to snake_case format

    Args:
        name (Str): camelCase string

    Returns:
        Str: snake_case string
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def camel_to_snake_dict(dict):
    """changes a dictionary from having camelCase keys to snake_case keys

    Args:
        dict (Dict[Any]): dictionary that uses camelCase formatted keys

    Returns:
        Dict[Any]: dictionary with snake_case fromatted keys
    """
    new_dict = {}
    for key, value in dict.items():
        new_dict[camel_to_snake(key)] = value
    return new_dict
