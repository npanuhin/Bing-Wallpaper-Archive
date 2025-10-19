import sys
import os

sys.path.append('../')
from cloudflare import CloudflareR2
from utils import mkpath


def main(root_path):
    storage = CloudflareR2()

    for root, dirs, files in os.walk(root_path):
        for file in sorted(files):
            file_path = mkpath(root, file)
            bucket_path = file_path.replace(root_path, '').replace('\\', '/').lstrip('/')
            storage.upload_file(file_path, bucket_path, skip_exists=True)


if __name__ == '__main__':
    main('../tmp/npanuhin-bing-wallpaper-archive')
