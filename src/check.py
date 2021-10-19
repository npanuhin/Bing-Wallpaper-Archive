from PIL import Image
import os

from utils import mkpath


US_SOURCE_IMAGES_PATH = mkpath("../", "api", "US", "images", "source")
US_1080P_IMAGES_PATH = mkpath("../", "api", "US", "images", "1080p")


def checkUSSourceImages(remove=False):
    print("Checking {}".format(US_SOURCE_IMAGES_PATH))

    for file in os.listdir(US_SOURCE_IMAGES_PATH):
        try:
            Image.open(mkpath(US_SOURCE_IMAGES_PATH, file))
        except IOError:
            print("{} is damaged".format(file))
            if remove:
                os.remove(mkpath(US_SOURCE_IMAGES_PATH, file))


def checkUS1080pImages(remove=False):
    print("Checking {}".format(US_1080P_IMAGES_PATH))

    for file in os.listdir(US_1080P_IMAGES_PATH):
        try:
            Image.open(mkpath(US_1080P_IMAGES_PATH, file))
        except IOError:
            print("{} is damaged".format(file))
            if remove:
                os.remove(mkpath(US_1080P_IMAGES_PATH, file))


if __name__ == "__main__":
    # checkUSSourceImages()
    checkUSSourceImages(remove=True)
    checkUS1080pImages(remove=True)
