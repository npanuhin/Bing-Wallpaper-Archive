import sys
import os

sys.path.append('../')
from Region import REGIONS  # noqa: E402
from utils import mkpath  # noqa: E402


WEBSITE_ROOT = '../website'


def main():
    for region in REGIONS:
        api = region.read_api()

        website_directory = mkpath(WEBSITE_ROOT, region.country.upper())

        os.makedirs(website_directory, exist_ok=True)

        for file in os.listdir(website_directory):
            os.remove(mkpath(website_directory, file))

        region.write_api(api, mkpath(website_directory, region.lang.lower() + '.json'))
        # region.write_api(
        #     api,
        #     mkpath(website_directory, region.lang.lower() + '.min.json'),
        #     indent=None, separators=(',', ':')
        # )

        # only_urls = {image['date']: image['url'] for image in api}

        # region.write_api(
        #     only_urls,
        #     mkpath(website_directory, region.lang.lower() + '.url.json'),
        #     indent=None, separators=(',', ':')
        # )

        # Split by year
        min_year = int(min(image['date'] for image in api).split('-')[0])
        max_year = int(max(image['date'] for image in api).split('-')[0])
        for year in range(min_year, max_year + 1):
            year_api = [image for image in api if image['date'].startswith(str(year))]
            region.write_api(
                year_api,
                mkpath(website_directory, region.lang.lower() + f'.{year}.json'),
                indent=None, separators=(',', ':')
            )


if __name__ == '__main__':
    main()
