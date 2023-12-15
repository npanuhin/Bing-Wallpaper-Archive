from posixpath import join as os_join, normpath as os_normpath
from subprocess import Popen, PIPE


def mkpath(*paths):
    return os_normpath(os_join(*paths))


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
