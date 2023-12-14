from json import loads as json_loads
from sys import path as sys_path
from PIL import Image
import os

sys_path.append("../")
from utils import mkpath


ROOT_PATH = mkpath("../", "../")

REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]


def check(path, remove=False):
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


def recursive_check(path, remove=False):
    images_path = mkpath(path)
    print("Checking {}".format(images_path))

    count = 0
    if os.path.isdir(images_path):
        for file in os.listdir(images_path):
            check(mkpath(images_path, file), remove)
            count += 1

    return count


def check_all(remove=False):
    count = 0
    print()
    for region in REGIONS:
        count += recursive_check(mkpath(ROOT_PATH, "api", region, "images"), remove)
        print()
    return count


def main(remove):
    if "GITHUB_CHANGED_FILES" not in os.environ:
        print("Checking all images...")
        print("Checked {} images".format(check_all(remove)))
        return

    print("Checking files {}...".format(os.environ["GITHUB_CHANGED_FILES"]))

    count = 0
    for file_path in json_loads(os.environ["GITHUB_CHANGED_FILES"]):
        if os.path.splitext(file_path)[1] in (".jpg", ".png"):
            check(mkpath(ROOT_PATH, file_path), remove)
            count += 1

    print("Checked {} images".format(count))


if __name__ == "__main__":
    main(remove=False)
