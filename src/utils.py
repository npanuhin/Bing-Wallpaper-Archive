from threading import Thread, Lock, active_count as threading_active_count
from posixpath import join as os_join, normpath as os_normpath
from json import load as json_load, dump as json_dump
from subprocess import Popen, PIPE
from calendar import monthrange
# from httplib2 import Http
from shutil import rmtree
from time import sleep
import datetime
import os


def mkpath(*paths):
    return os_normpath(os_join(*paths))


def _pass(*args, **kwargs):
    pass


def clear_folder(path, folders=False):
    for item in os.listdir(mkpath(path)):

        if os.path.isfile(mkpath(path, item)):
            os.remove(mkpath(path, item))

        elif os.path.isdir(mkpath(path, item)):
            rmtree(mkpath(path, item))


def create_folder_if_absent(path):
    if not os.path.isdir(mkpath(path)):
        os.makedirs(mkpath(path))


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, monthrange(year, month)[1])
    return datetime.date(year, month, day)


def remove_metadata(path, extension="jpg", exiftool=mkpath("exiftool", "exiftool")):
    print('Removing metadata in "{}"...'.format(path))
    s = Popen(
        "\"{}\" -all= --icc_profile:all -overwrite_original -progress -ext \"{}\" \"{}\"".format(exiftool, extension, path),
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    ).communicate()

    s = list(map(lambda x: x.decode("cp1251"), s))

    print(s)


# class FileDownloader:
#     def __init__(self):
#         self.h = Http('cache/.http_cache')
#         self.thread_lock = Lock()

#     def download(self, url, path):
#         with self.thread_lock:
#             with open(mkpath(path), 'wb') as file:
#                 response, content = self.h.request(url)
#                 file.write(content)

#     def __del__(self):
#         if os.path.isdir('cache/.http_cache'):
#             rmtree('cache/.http_cache')


class SafeJson:
    def __init__(self):
        self.default_cache_timer = 500  # > 1 is unsafe

        self.thread_lock = Lock()
        self.cache = {}
        self.cache_timer = self.default_cache_timer

    # def __del__(self):
    #     '''Not working: "open" has already been deleted by the GC'''
    #     self.dump_cache()

    def dump(self, path, data, allow_cache=False, ensure_ascii=False, prettify=False, *args, **kwargs):
        kwargs["ensure_ascii"] = ensure_ascii
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


def prettify_data_string(string):
    return string.replace("\r\n", '\n').replace("\n\r", '\n').replace('\xa0', ' ').strip()
