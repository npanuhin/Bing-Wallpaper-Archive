from subprocess import Popen, PIPE
import pathlib
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


def posixpath(path: str) -> str:
    return pathlib.Path(path).as_posix()


def remove_metadata(path, extension='jpg', exiftool='exiftool/exiftool'):
    print(f'Removing metadata in "{path}"...')
    s = Popen(
        # exiftool -all= --icc_profile:all -overwrite_original -progress -ext jpg -r "../api"  [recursive]
        f'"{exiftool}" -all= --icc_profile:all -overwrite_original -progress -ext "{extension}" "{path}"',
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    ).communicate()

    s = [item.decode('cp1251') for item in s]

    print(s)
