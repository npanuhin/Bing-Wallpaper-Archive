from pathlib import Path
import os

import requests


def mkpath(*paths: str):
    return os.path.normpath(os.path.join(*paths))


SRC_PATH = mkpath(os.path.dirname(__file__))
ROOT_PATH = mkpath(SRC_PATH, '../')
API_PATH = mkpath(ROOT_PATH, 'api')
CONFIGS_PATH = mkpath(SRC_PATH, 'configs')
WEBSITE_CONTENT_PATH = mkpath(SRC_PATH, 'website', 'root')


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
