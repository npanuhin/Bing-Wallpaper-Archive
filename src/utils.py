from typing import Any
import pathlib
import json
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


SRC = mkpath(os.path.dirname(__file__))
HOME = mkpath(SRC, '../')
API_HOME = mkpath(HOME, 'api')


def posixpath(path: str) -> str:
    return pathlib.Path(path).as_posix()


def debug(name: str, obj: Any):
    with open(mkpath(SRC, 'debug', f'{name}.txt'), 'w', encoding='utf-8') as file:
        file.write(str(obj))


def debug_json(name: str, obj: tuple | list | dict):
    debug(name, json.dumps(obj, ensure_ascii=False, indent=4))
