from PIL import Image
import os

from utils import mkpath

API_PATH = mkpath("../", "api")

REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]


def checkImage(path, remove=False):
    try:
        Image.open(path)
    except IOError:
        print("{} is damaged".format(path))
        if remove:
            os.remove(path)
            print("Removed {}".format(path))
        return False
    return True


def checkSourceImages(region, remove=False):
    images_path = mkpath(API_PATH, region, "images", "source")
    print("Checking {}".format(images_path))

    for file in os.listdir(images_path):
        checkImage(mkpath(images_path, file), remove)


def check1080pImages(region, remove=False):
    images_path = mkpath(API_PATH, region, "images", "1080p")
    print("Checking {}".format(images_path))

    for file in os.listdir(images_path):
        checkImage(mkpath(images_path, file), remove)


def checkAll(remove=False):
    for region in REGIONS:
        checkSourceImages(region, remove)
        check1080pImages(region, remove)
        print()


if __name__ == "__main__":
    checkAll(remove=False)
