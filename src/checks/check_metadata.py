from subprocess import Popen, PIPE
from sys import path as sys_path
import re

sys_path.append("../")
from utils import mkpath


API_PATH = mkpath("../", "../", "api")
EXIFTOOL = mkpath("../", "exiftool", "exiftool")


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


if __name__ == "__main__":
    recursive_check(API_PATH)
