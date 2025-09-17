import shutil
import sys
import os

sys.path.append('../')
from Region import REGIONS, ROW  # noqa: E402
from utils import SRC, mkpath  # noqa: E402


WEBSITE_ROOT = mkpath(SRC, 'website/root/_website')


def build():
    for region in REGIONS:
        region_directory = mkpath(WEBSITE_ROOT, region.api_country.upper())
        api = region.read_api()

        # Clean folder
        if os.path.isdir(region_directory):
            shutil.rmtree(region_directory)

        os.makedirs(region_directory, exist_ok=True)

        # Add APIs
        region.write_api(api, mkpath(region_directory, region.api_lang.lower() + '.json'))

        if api:
            # Split by year
            min_year = int(min(image['date'] for image in api).split('-')[0])
            max_year = int(max(image['date'] for image in api).split('-')[0])
            for year in range(min_year, max_year + 1):
                year_api = [image for image in api if image['date'].startswith(str(year))]
                region.write_api(
                    year_api,
                    mkpath(region_directory, region.api_lang.lower() + f'.{year}.json'),
                    indent=None, separators=(',', ':')
                )

    # Place starting image
    with open(mkpath(WEBSITE_ROOT, 'index.source.html'), 'r', encoding='utf-8') as file:
        html = file.read().format(
            starting_image=ROW.read_api()[-1]['url'],
            starting_title=ROW.read_api()[-1]['title'],
            starting_description=ROW.read_api()[-1]['description']
        )

    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(html)


if __name__ == '__main__':
    build()
