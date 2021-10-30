from PIL import Image
import os

from utils import mkpath


US_SOURCE_IMAGES_PATH = mkpath("../", "api", "US", "images", "source")
US_1080P_IMAGES_PATH = mkpath("../", "api", "US", "images", "1080p")


def checkImage(path, remove=False):
    try:
        Image.open(path)
    except IOError:
        print("{} is damaged".format(path))
        if remove:
            os.remove(path)
        return False
    return True


def checkUSSourceImages(remove=False):
    print("Checking {}".format(US_SOURCE_IMAGES_PATH))

    for file in os.listdir(US_SOURCE_IMAGES_PATH):
        checkImage(mkpath(US_SOURCE_IMAGES_PATH, file), remove)


def checkUS1080pImages(remove=False):
    print("Checking {}".format(US_1080P_IMAGES_PATH))

    for file in os.listdir(US_1080P_IMAGES_PATH):
        checkImage(mkpath(US_1080P_IMAGES_PATH, file), remove)


if __name__ == "__main__":
    # checkUSSourceImages()
    checkUSSourceImages(remove=False)
    checkUS1080pImages(remove=False)
