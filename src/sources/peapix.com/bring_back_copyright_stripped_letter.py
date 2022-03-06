from sys import path as sys_path
sys_path.append("../")

from utils import mkpath, SafeJson
from copy import deepcopy
from math import floor
import re


API_PATH = mkpath("../../api/")
REGION = "US"
safe_json = SafeJson()

old_api = safe_json.load(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".json"))
size = len(old_api)
changed = 0

# ================================ Changes ================================

new_api = deepcopy(old_api)

for item in new_api:
    copyright = item["copyright"]

    if copyright is None:
        continue

    assert isinstance(copyright, str), "Copyright type is not str but {} for {}".format(
        type(copyright), item["date"]
    )

    copyright = re.sub(
        r"^(.+[\/\\])(Getty\s*Image|Minden\s*Picture)$",
        r"\1\2s",
        copyright,
        1, re.DOTALL | re.IGNORECASE | re.UNICODE
    )

    copyright = re.sub(
        r"^(.+[\/\\])(Alam)$",
        r"\1\2y",
        copyright,
        1, re.DOTALL | re.IGNORECASE | re.UNICODE
    )

    item["copyright"] = copyright


# ================================ Checks =================================

def check_changed(old_api, new_api):
    if old_api["copyright"] != new_api["copyright"]:
        return True

    if old_api["copyright"] is None:
        # print("{} has no copyright".format(old_api["date"]))
        return True

    if old_api["copyright"].endswith("©"):
        return True

    return False


for i in range(size):
    if check_changed(old_api[i], new_api[i]):
        changed += 1
    else:
        print("{} is unchanged".format(old_api[i]["date"]))
        pass

print("Changed: {}/{} ({}%)".format(changed, size, floor(changed / size * 100 * 100) / 100))
