import pathlib
import json
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


def posixpath(path: str) -> str:
    return pathlib.Path(path).as_posix()


def debug(name: str, obj):
    with open(mkpath(os.path.dirname(__file__), 'debug', f'{name}.txt'), 'w', encoding='utf-8') as file:
        file.write(str(obj))


def debug_json(name: str, obj):
    debug(name, json.dumps(obj, ensure_ascii=False, indent=4))
