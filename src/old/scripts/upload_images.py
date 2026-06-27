import sys
import os

sys.path.append('../')
from system_utils import mkpath, posixpath
from Region import REGIONS
from gcloud import GCloud


def main():
    gcloud = GCloud()

    for region in REGIONS:
        api = region.read_api()

        for item in api:
            if os.path.isfile(item['path']):
                item['url'] = gcloud.upload_file(
                    item['path'], posixpath(mkpath(region.gcloud_images_path, item['date'] + '.jpg')), skip_exists=True
                )

        region.write_api(api)


if __name__ == '__main__':
    main()
