import os

from dotenv import load_dotenv


GAME_DATA_ENV_VAR = 'GAME_DATA_ENV'

_mode: bool | None = None


def set_mode(prod: bool):
    global _mode
    _mode = not prod
    os.environ[GAME_DATA_ENV_VAR] = 'prod' if prod else 'dev'


def is_dev() -> bool:
    if _mode is not None:
        return _mode

    env = os.environ.get(GAME_DATA_ENV_VAR, 'dev').lower()
    return env != 'prod'


def is_prod() -> bool:
    return not is_dev()


def load_env():
    if is_prod():
        load_dotenv('.env.prod')
    else:
        load_dotenv('.env.dev')
