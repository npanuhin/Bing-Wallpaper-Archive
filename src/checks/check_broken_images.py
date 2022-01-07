from sys import path as sys_path
from PIL import Image
import os

sys_path.append("../")
from utils import mkpath

API_PATH = mkpath("../", "../", "api")

REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]


def check_image(path, remove=False):
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
    count = 0

    if os.path.isdir(images_path):
        for file in os.listdir(images_path):
            check_image(mkpath(images_path, file), remove)
            count += 1
    return count


def checkAll(remove=False):
    count = 0
    for region in REGIONS:
        count += recursiveCheck(mkpath(API_PATH, region, "images"), remove)
        print()
    return count


if __name__ == "__main__":
    print("Checked {} images".format(checkAll(remove=False)))
