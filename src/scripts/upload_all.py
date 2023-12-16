import sys
import os

sys.path.append('../')
from Region import REGIONS  # noqa: E402
from gcloud import GCloud  # noqa: E402
from utils import mkpath  # noqa: E402


def main():
    gcloud = GCloud()

    for region in REGIONS:
        api = region.read_api()

        for item in api:
            image_path = mkpath(region.images_path, item['date'] + '.jpg')
            if os.path.isfile(image_path):
                item['url'] = gcloud.upload_file(image_path, item['path'], skip_exists=True)

        region.write_api(api)


if __name__ == '__main__':
    main()
