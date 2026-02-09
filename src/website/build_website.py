from io import BytesIO
import base64
import shutil
import sys
import os

from PIL import Image, ImageDraw
import requests

sys.path.append('../')
from system_utils import mkpath, WEBSITE_PATH
from Region import REGIONS, ROW

WEBSITE_SOURCES_ROOT = mkpath(WEBSITE_PATH, 'src')
WEBSITE_SYS_ROOT = mkpath(WEBSITE_PATH, 'root')
WEBSITE_ROOT = mkpath(WEBSITE_PATH, 'root', '_website')
WEBSITE_ASSETS_PATH = mkpath(WEBSITE_ROOT, 'assets')

LATEST_IMAGE_SVG_TEMPLATE = mkpath(WEBSITE_PATH, 'latest-template.svg')

WEBSITE_INITIAL_IMAGE_PATH = mkpath(WEBSITE_ASSETS_PATH, 'initial-image.jpg')

INITIAL_IMAGE_WIDTH = 1920
INITIAL_IMAGE_HEIGHT = 1080

README_IMAGE_WEBP_PATH = mkpath(WEBSITE_ROOT, 'latest.webp')
README_IMAGE_SVG_PATH = mkpath(WEBSITE_ROOT, 'latest.svg')
README_IMAGE_RADIUS = 30  # Based on height=1080


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
                    minify=True
                )

    # ==================== Initial image ====================
    initial_image_data = ROW.read_api()[-1]

    assert initial_image_data.url is not None  # TODO
    image_response = requests.get(initial_image_data.url)

    # Generate WebP with rounded corners
    with Image.open(BytesIO(image_response.content)) as img:
        img = img.convert('RGBA')
        width, height = img.size
        radius = round(height * README_IMAGE_RADIUS / INITIAL_IMAGE_HEIGHT)

        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + img.size, radius=radius, fill=255)
        img.putalpha(mask)

        img.save(README_IMAGE_WEBP_PATH, 'webp', quality=80, method=6)

    # Generate SVG with rounded corners
    with open(LATEST_IMAGE_SVG_TEMPLATE, 'r') as file:
        svg_template = file.read()

    base64_image = base64.b64encode(image_response.content).decode('utf-8')
    image_data_uri = f'data:image/jpeg;base64,{base64_image}'

    svg_content = (svg_template
                   .replace('{width}', str(width))
                   .replace('{height}', str(height))
                   .replace('{radius}', str(radius))
                   .replace('{image_url}', image_data_uri))

    with open(README_IMAGE_SVG_PATH, 'w') as file:
        file.write(svg_content)

    # Generate website's initial image
    os.makedirs(WEBSITE_ASSETS_PATH, exist_ok=True)

    with Image.open(BytesIO(image_response.content)) as img:
        img = img.convert('RGB')

        original_width, original_height = img.size

        width_ratio = INITIAL_IMAGE_WIDTH / original_width
        height_ratio = INITIAL_IMAGE_HEIGHT / original_height

        if width_ratio >= height_ratio:
            new_width = INITIAL_IMAGE_WIDTH
            new_height = round(original_height * width_ratio)
        else:
            new_height = INITIAL_IMAGE_HEIGHT
            new_width = round(original_width * height_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        img.save(WEBSITE_INITIAL_IMAGE_PATH, 'jpeg', quality=60, optimize=True)

    # Generate website's HTML
    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'r', encoding='utf-8') as file:
        html = file.read()

    html = (html
            .replace('{initial_title}', initial_image_data.title or '')
            .replace('{initial_image_url}', initial_image_data.url or '')
            .replace('{initial_description}', initial_image_data.description or '')
            )

    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(html)

    # Add headers
    shutil.copyfile(
        mkpath(WEBSITE_PATH, '_headers'),
        mkpath(WEBSITE_SYS_ROOT, '_headers')
    )


if __name__ == '__main__':
    build_website()
