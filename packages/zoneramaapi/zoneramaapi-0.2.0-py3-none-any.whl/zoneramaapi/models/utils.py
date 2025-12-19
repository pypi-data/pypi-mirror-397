import re


def to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def map_key(field_map: dict, api_key: str) -> str:
    return field_map.get(api_key, to_snake(api_key))
