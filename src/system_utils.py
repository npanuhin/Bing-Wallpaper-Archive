from pathlib import Path
from threading import Lock
from typing import Any, NoReturn
import builtins
import os

import requests


def mkpath(*paths: str):
    return os.path.normpath(os.path.join(*paths))


class PATH:
    SRC = mkpath(os.path.dirname(__file__))
    ROOT = mkpath(SRC, '../')
    API = mkpath(ROOT, 'api')
    CONFIGS = mkpath(SRC, 'configs')

    WEBSITE = mkpath(SRC, 'website')
    WEBSITE_ROOT = mkpath(WEBSITE, 'root', '_website')


def posixpath(path: str) -> str:
    return Path(path).as_posix()


_PRINT_LOCK = Lock()
_builtin_print = builtins.print


def print_async(*args: Any, **kwargs: Any) -> None:
    with _PRINT_LOCK:
        _builtin_print(*args, **kwargs)


builtins.print = print_async


def warn(message: str):
    print(f'\n⚠ Warning ⚠\n{message}\n')


def error(message: str) -> NoReturn:
    print(f'\n✖ Error ✖\n{message}\n')
    raise RuntimeError(message)


def fetch_json(url: str, *args, **kwargs):
    r = requests.get(url, *args, **kwargs)
    try:
        return r.json()
    except Exception:
        error(f'Failed to fetch JSON from {r.url}')
