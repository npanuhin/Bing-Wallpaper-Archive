from exif import Image as ExifImage
from PIL import Image
import os

from utils import mkpath, createFolderIfAbsent

API_PATH = mkpath("../", "api")

REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]


def removeMetadata(path, remove=False):
    with open(path, "rb") as file:
        image = ExifImage(file)

    if image.has_exif:
        print(image.exif_version)
        image.delete_all()
        with open(path, "wb") as file:
            file.write(image.get_file())
    else:
        print("no exif")


def removeAll(remove=False):
    for region in REGIONS:
        images_path = createFolderIfAbsent(mkpath(API_PATH, region, "images"))
        for file in os.listdir(images_path):
            print("Checking metadata for {}".format(mkpath(images_path, file)))
            removeMetadata(mkpath(images_path, file), remove)

            # exit()
            # break


if __name__ == "__main__":
    removeAll(remove=False)
