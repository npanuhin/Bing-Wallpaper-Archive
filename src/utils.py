import pathlib
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


def posixpath(path: str) -> str:
    return pathlib.Path(path).as_posix()
