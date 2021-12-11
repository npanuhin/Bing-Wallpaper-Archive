from sys import path as sys_path
from PIL import Image
import os

sys_path.append("../")
from utils import mkpath

API_PATH = mkpath("../", "../", "api")

REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]


def checkImage(path, remove=False):
    try:
        Image.open(path)
    except IOError:
        if remove:
            os.remove(path)
            print("Removed {}".format(path))
        else:
            raise ValueError("{} is damaged".format(path))
        return False
    return True


def recursiveCheck(path, remove=False):
    images_path = mkpath(path)
    print("Checking {}".format(images_path))

    if os.path.isdir(images_path):
        for file in os.listdir(images_path):
            checkImage(mkpath(images_path, file), remove)


def checkAll(remove=False):
    for region in REGIONS:
        recursiveCheck(mkpath(API_PATH, region, "images"), remove)
        print()


if __name__ == "__main__":
    checkAll(remove=False)
