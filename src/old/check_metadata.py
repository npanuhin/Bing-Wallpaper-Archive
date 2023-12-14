from json import loads as json_loads
from subprocess import Popen, PIPE
from sys import path as sys_path
import re
import os

sys_path.append("../")
from utils import mkpath


ROOT_PATH = mkpath("../", "../")
EXIFTOOL = mkpath("../", "exiftool", "exiftool")


def check(path):
    s = Popen(
        "\"{}\" -all= --icc_profile:all -overwrite_original -progress \"{}\"".format(EXIFTOOL, mkpath(path)),
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    ).communicate()

    s = ''.join(map(lambda x: x.decode("cp1251"), s))

    print(s)

    changed = int(re.search(r"(\d+)\s+image\s*files\s*updated", s, re.IGNORECASE).group(1))

    assert changed == 0, "{} images have metadata".format(changed)

    print("Success")


def recursive_check(path):
    s = Popen(
        "\"{}\" -all= --icc_profile:all -overwrite_original -progress -ext jpg -r \"{}\"".format(EXIFTOOL, mkpath(path)),
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    ).communicate()

    s = ''.join(map(lambda x: x.decode("cp1251"), s))

    print(s)

    changed = int(re.search(r"(\d+)\s+image\s*files\s*updated", s, re.IGNORECASE).group(1))

    assert changed == 0, "{} images have metadata".format(changed)

    print("Success")


def check_all():
    recursive_check(mkpath(ROOT_PATH, "api"))


def main():
    if "GITHUB_CHANGED_FILES" not in os.environ:
        print("Checking all images...")
        check_all()
        return

    print("Checking files {}...".format(os.environ["GITHUB_CHANGED_FILES"]))

    count = 0
    for file_path in json_loads(os.environ["GITHUB_CHANGED_FILES"]):
        if os.path.splitext(file_path)[1] in (".jpg", ".png"):
            check(mkpath(ROOT_PATH, file_path))
            count += 1

    print("Checked {} images".format(count))


if __name__ == "__main__":
    main()
