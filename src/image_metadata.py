from subprocess import Popen, PIPE
from time import sleep
import os

from utils import mkpath, SafeJson, Threads

REMOVE_METADATA_CACHE_PATH = "cache/remove_metadata.cache"

safeJson = SafeJson()


def removeMetadata(path, extension="jpg"):
    s = Popen(
        "exiftool -all= --icc_profile:all -overwrite_original -progress -ext {} -r \"{}\"".format(extension, path),
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    ).communicate()

    s = list(map(lambda x: x.decode("cp1251"), s))

    print(path, ": ", s, sep='')


def removeMetadataThread(data, path):
    # print(path)
    removeMetadata(path, os.path.splitext(path)[1])
    data.add(path)
    safeJson.dump(mkpath(REMOVE_METADATA_CACHE_PATH), sorted(data), prettify=True)


def recursiveRemoveMetadata(path):
    print("Removing metadata in /api...")
    if os.path.isfile(mkpath(REMOVE_METADATA_CACHE_PATH)):
        data = set(safeJson.load(mkpath(REMOVE_METADATA_CACHE_PATH)))
    else:
        data = set()

    with Threads() as threads:
        for path, folders, files in os.walk(mkpath(path)):
            for file in files:
                if os.path.splitext(file)[1] in (".jpg", ".png"):

                    if mkpath(path, file) not in data:
                        while threads.active_count() >= 5:
                            sleep(0.1)

                        threads.add(removeMetadataThread, (data, mkpath(path, file))).start()


if __name__ == "__main__":
    recursiveRemoveMetadata("../api")
