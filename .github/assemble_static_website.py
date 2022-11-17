# Delete everything we don't need on the final website

from itertools import chain
import shutil
import os

include = [
    "src/website/"
]


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


for i in range(len(include)):
    include[i] = mkpath(include[i])
    assert os.path.exists(include[i])

for cur_path, folders, files in os.walk('.'):
    for objname in chain(folders, files):
        objpath = mkpath(cur_path, objname)
        if any(
            objpath.startswith(test_path) or test_path.startswith(objpath)
            for test_path in map(mkpath, include)
        ):
            continue
        if os.path.isdir(objpath):
            shutil.rmtree(objpath)
        else:
            os.remove(objpath)
        print(f"Removed {objpath}")
