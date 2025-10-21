import sys
import os

sys.path.append('../')
from Region import REGIONS, ROW
from utils import mkpath, WEBSITE_PATH


WEBSITE_SOURCES_ROOT = mkpath(WEBSITE_PATH, 'src')
WEBSITE_ROOT = mkpath(WEBSITE_PATH, 'root', '_website')


def build_website():
    if not os.path.isdir(WEBSITE_ROOT):
        sys.stderr.write(f'Error: Build directory "{WEBSITE_ROOT}" not found.\n')
        sys.stderr.write('Please build the website before this script.\n')
        sys.exit(1)

    for region in REGIONS:
        region_directory = mkpath(WEBSITE_ROOT, region.api_country.upper())
        api = region.read_api()

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
    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'r', encoding='utf-8') as file:
        html = file.read()

    html = (html
            .replace('{initial_title}', initial_image_data.title or '')
            .replace('{initial_image_url}', initial_image_data.url or '')
            .replace('{initial_description}', initial_image_data.description or '')
    )

    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(html)


if __name__ == '__main__':
    build_website()
