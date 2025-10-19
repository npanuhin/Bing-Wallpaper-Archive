from pathlib import Path
import os

import requests


def mkpath(*paths: str):
    return os.path.normpath(os.path.join(*paths))


SRC = mkpath(os.path.dirname(__file__))
HOME = mkpath(SRC, '../')
API_HOME = mkpath(HOME, 'api')


def posixpath(path: str) -> str:
    return Path(path).as_posix()

def warn(message: str):
    print(f'\n⚠ Warning ⚠\n{message}\n')

def fetch_json(url: str, *args, **kwargs):
    r = requests.get(url, *args, **kwargs)
    try:
        return r.json()
    except Exception:
        warn(f'Failed to fetch JSON from {r.url}')
        raise
