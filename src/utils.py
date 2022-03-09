from posixpath import join as os_join, normpath as os_normpath
from subprocess import Popen, PIPE


def mkpath(*paths):
    return os_normpath(os_join(*paths))


def remove_metadata(path, extension="jpg", exiftool=mkpath("exiftool", "exiftool")):
    print('Removing metadata in "{}"...'.format(path))
    s = Popen(
        # exiftool -all= --icc_profile:all -overwrite_original -progress -ext jpg -r "../api"  [recursive]
        "\"{}\" -all= --icc_profile:all -overwrite_original -progress -ext \"{}\" \"{}\"".format(exiftool, extension, path),
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    ).communicate()

    s = list(map(lambda x: x.decode("cp1251"), s))

    print(s)
