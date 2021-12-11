from threading import Thread, Lock, active_count as threading_active_count
from json import load as json_load, dump as json_dump
from calendar import monthrange
from shutil import rmtree
from time import sleep
import httplib2
import datetime
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


def clearFolder(path, folders=False):
    for item in os.listdir(mkpath(path)):

        if os.path.isfile(mkpath(path, item)):
            os.remove(mkpath(path, item))

        elif os.path.isdir(mkpath(path, item)):
            rmtree(mkpath(path, item))


def createFolderIfAbsent(path):
    if not os.path.isdir(mkpath(path)):
        os.makedirs(mkpath(path))


def addMonths(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, monthrange(year, month)[1])
    return datetime.date(year, month, day)


class FileDownloader:
    def __init__(self):
        self.h = httplib2.Http('.cache')
        self.thread_lock = Lock()

    def download(self, url, path):
        with self.thread_lock:
            with open(mkpath(path), 'wb') as file:
                response, content = self.h.request(url)
                file.write(content)

    def __del__(self):
        if os.path.isdir('.cache'):
            rmtree('.cache')


class SafeJson:
    def __init__(self):
        self.default_cache_timer = 500  # > 1 is unsafe

        self.thread_lock = Lock()
        self.cache = {}
        self.cache_timer = self.default_cache_timer

    # def __del__(self):
    #     '''Not working: "open" has already been deleted by the GC'''
    #     self.dump_cache()

    def dump(self, path, data, allow_cache=False, prettify=False, *args, **kwargs):
        self.cache[os.path.abspath(mkpath(path))] = (data, prettify, args, kwargs)

        self.cache_timer -= 1
        if not allow_cache or self.cache_timer == 0:
            self.dump_cache()

    def dump_cache(self):
        self.cache_timer = self.default_cache_timer

        for filepath, content in self.cache.items():
            data, prettify, args, kwargs = content
            with self.thread_lock:
                with open(filepath, 'w', encoding="utf-8") as file:
                    if prettify:
                        json_dump(data, file, indent=4, *args, **kwargs)
                    else:
                        json_dump(data, file, separators=(',', ':'), *args, **kwargs)

        self.cache = {}

    def load(self, path, *args, **kwargs):
        with self.thread_lock:
            with open(os.path.abspath(mkpath(path)), 'r', encoding="utf-8") as file:
                data = json_load(file, *args, **kwargs)

        return data


class Threads:
    def __init__(self):
        self.threads = []

    def __del__(self):
        self.join()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.join()

    def add(self, target, args, **kwargs):
        self.threads.append(Thread(target=target, args=args, **kwargs))
        return self.threads[-1]

    def join(self):
        for t in self.threads:
            t.join()

    def active_count(self):
        return threading_active_count()

    def wait_free(self, count):
        while threading_active_count() > count:
            sleep(0.01)


def prettifyDataString(string):
    return string.replace("\r\n", '\n').replace("\n\r", '\n').replace('\xa0', ' ').strip()
