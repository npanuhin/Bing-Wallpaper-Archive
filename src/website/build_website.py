import shutil
import sys
import os

sys.path.append('../')
from Region import REGIONS, ROW
from utils import mkpath, WEBSITE_CONTENT_PATH


WEBSITE_ROOT = mkpath(WEBSITE_CONTENT_PATH, '_website')


def build_website():
    for region in REGIONS:
        region_directory = mkpath(WEBSITE_ROOT, region.api_country.upper())
        api = region.read_api()

        # Clean folder
        if os.path.isdir(region_directory):
            shutil.rmtree(region_directory)

        os.makedirs(region_directory, exist_ok=True)

        # Add API
        region.write_api(api, mkpath(region_directory, region.api_lang.lower() + '.json'))

        if api:
            # Split by year
            min_year = min(image.date for image in api).year
            max_year = max(image.date for image in api).year

            for year in range(min_year, max_year + 1):
                api_for_year = [image for image in api if image.date.year == year]
                region.write_api(
                    api_for_year,
                    mkpath(region_directory, region.api_lang.lower() + f'.{year}.json'),
                    indent=None, separators=(',', ':')  # Compact JSON
                )

    # Place the starting image
    initial_image_data = ROW.read_api()[-1]
    with open(mkpath(WEBSITE_ROOT, 'index.source.html'), 'r', encoding='utf-8') as file:
        html = file.read().format(
            initial_title=initial_image_data.title,
            initial_image_url=initial_image_data.url,
            initial_description=initial_image_data.description
        )

    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(html)


if __name__ == '__main__':
    build_website()
