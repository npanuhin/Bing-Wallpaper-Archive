from json import dump as json_dump
from shutil import rmtree
import httplib2
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


def clearFolder(path, folders=False):
    for item in os.listdir(mkpath(path)):

        if os.path.isfile(mkpath(path, item)):
            os.remove(mkpath(path, item))

        elif os.path.isdir(mkpath(path, item)):
            rmtree(mkpath(path, item))


class ImageDownloader:
    def __init__(self):
        self.h = httplib2.Http('.cache')

    def download(self, url, path):
        with open(path, 'wb') as file:
            response, content = self.h.request(url)
            file.write(content)

    def __del__(self):
        if os.path.isdir('.cache'):
            rmtree('.cache')


def safeDumpJson(path, data, *args, **kwargs):
    with open(mkpath(path) + ".replace", 'w', encoding="utf-8") as file:
        json_dump(data, file, *args, **kwargs)

    while True:
        try:
            os.replace(
                mkpath(path) + ".replace",
                mkpath(path)
            )
        except PermissionError:
            continue
        break
