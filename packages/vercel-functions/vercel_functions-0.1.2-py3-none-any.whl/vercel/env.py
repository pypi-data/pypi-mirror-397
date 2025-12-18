from os import environ


def __getattr__(key: str) -> str:
    return environ[key]
