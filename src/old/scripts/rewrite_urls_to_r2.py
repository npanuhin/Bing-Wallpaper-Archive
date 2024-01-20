import sys

sys.path.append('../')
from Region import REGIONS  # noqa: E402


# https://storage.googleapis.com/npanuhin-bing-wallpaper-archive/US/en/2010-01-01.jpg
# https://bing.npanuhin.me/US/en/2010-01-01.jpg


def check_storage():
    for region in REGIONS:
        api = region.read_api()

        for item in api:
            item['url'] = item['url'].replace(
                'https://storage.googleapis.com/npanuhin-bing-wallpaper-archive',
                'https://bing.npanuhin.me'
            )

        region.write_api(api)


if __name__ == '__main__':
    check_storage()
