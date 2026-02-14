from dataclasses import asdict
from io import BytesIO
import argparse
import shutil
import base64
import sys
import os

from PIL import Image, ImageDraw
import requests

sys.path.append('../')
from system_utils import mkpath, WEBSITE_PATH, WEBSITE_ROOT
from structures import ApiEntry
from Region import REGIONS
from api import write_json

WEBSITE_SOURCES_ROOT = mkpath(WEBSITE_PATH, 'src')
WEBSITE_SYS_ROOT = mkpath(WEBSITE_PATH, 'root')
WEBSITE_ASSETS_PATH = mkpath(WEBSITE_ROOT, 'assets')

LATEST_IMAGE_SVG_TEMPLATE = mkpath(WEBSITE_PATH, 'latest-template.svg')

WEBSITE_INITIAL_IMAGE_PATH = mkpath(WEBSITE_ASSETS_PATH, 'initial-image.jpg')

INITIAL_IMAGE_WIDTH = 1920
INITIAL_IMAGE_HEIGHT = 1080

README_IMAGE_WEBP_PATH = mkpath(WEBSITE_ROOT, 'latest.webp')
README_IMAGE_SVG_PATH = mkpath(WEBSITE_ROOT, 'latest.svg')
README_IMAGE_RADIUS = 30  # Based on height=1080


def gen_api_endpoints(region_to_api: dict[str, list[ApiEntry]]):
    all_json_data = {
        region_id: [asdict(entry) for entry in api]
        for region_id, api in region_to_api.items()
    }

    # /all.json
    write_json(all_json_data, mkpath(WEBSITE_ROOT, 'all.json'))
    write_json(all_json_data, mkpath(WEBSITE_ROOT, 'all.min.json'), minify=True)

    for region_id, api in region_to_api.items():
        country, lang = region_id.split('-')
        api_json = all_json_data[region_id]

        # /{country}-{language}.json
        write_json(api_json, mkpath(WEBSITE_ROOT, f'{region_id}.json'))
        write_json(api_json, mkpath(WEBSITE_ROOT, f'{region_id}.min.json'), minify=True)

        # backward compatibility: /{country}/{language}
        write_json(api_json, mkpath(WEBSITE_ROOT, country, f'{lang}.json'))
        write_json(api_json, mkpath(WEBSITE_ROOT, country, f'{lang}.min.json'), minify=True)

        # By year
        years = sorted(set(entry.date.year for entry in api))
        for year in years:
            api_year_json = [
                entry_json
                for entry, entry_json in zip(api, api_json)
                if entry.date.year == year
            ]

            write_json(api_year_json, mkpath(WEBSITE_ROOT, f'{region_id}.{year}.json'))
            write_json(api_year_json, mkpath(WEBSITE_ROOT, f'{region_id}.{year}.min.json'), minify=True)

            # backward compatibility: /{country}/{language}
            write_json(api_year_json, mkpath(WEBSITE_ROOT, country, f'{lang}.{year}.json'))
            write_json(api_year_json, mkpath(WEBSITE_ROOT, country, f'{lang}.{year}.min.json'), minify=True)

        # By month
        months = sorted(set((entry.date.year, entry.date.month) for entry in api))
        for year, month in months:
            api_month_json = [
                entry_json
                for entry, entry_json in zip(api, api_json)
                if entry.date.year == year and entry.date.month == month
            ]
            month_str = f'{month:02d}'

            write_json(api_month_json, mkpath(WEBSITE_ROOT, f'{region_id}.{year}.{month_str}.json'))
            write_json(api_month_json, mkpath(WEBSITE_ROOT, f'{region_id}.{year}.{month_str}.min.json'), minify=True)

            # backward compatibility: /{country}/{language}
            write_json(api_month_json, mkpath(WEBSITE_ROOT, country, f'{lang}.{year}.{month_str}.min.json'))
            write_json(api_month_json, mkpath(WEBSITE_ROOT, country, f'{lang}.{year}.{month_str}.json'), minify=True)


def gen_github_initial_image(image_content: bytes):
    # Generate WebP with rounded corners
    with Image.open(BytesIO(image_content)) as img:
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

    base64_image = base64.b64encode(image_content).decode('utf-8')
    image_data_uri = f'data:image/jpeg;base64,{base64_image}'

    svg_content = (svg_template
                   .replace('{width}', str(width))
                   .replace('{height}', str(height))
                   .replace('{radius}', str(radius))
                   .replace('{image_url}', image_data_uri))

    with open(README_IMAGE_SVG_PATH, 'w') as file:
        file.write(svg_content)


def gen_website_initial_image(image_content: bytes):
    os.makedirs(WEBSITE_ASSETS_PATH, exist_ok=True)

    with Image.open(BytesIO(image_content)) as img:
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


def update_website_html(initial_image_data: ApiEntry):
    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'r', encoding='utf-8') as file:
        html = file.read()

    html = (html
            .replace('{initial_title}', initial_image_data.title or '')
            .replace('{initial_image_url}', initial_image_data.url or '')
            .replace('{initial_description}', initial_image_data.description or '')
            )

    with open(mkpath(WEBSITE_ROOT, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(html)


def add_headers():
    shutil.copyfile(
        mkpath(WEBSITE_PATH, '_headers'),
        mkpath(WEBSITE_SYS_ROOT, '_headers')
    )


def build_website(*, dev: bool = False):
    if not os.path.isdir(WEBSITE_ROOT):
        sys.stderr.write(f'Error: Build directory "{WEBSITE_ROOT}" not found.\n')
        sys.stderr.write('Please build the website before this script.\n')
        sys.exit(1)

    region_to_api = {
        f'{region.api_country}-{region.api_lang}': region.read_api()
        for region in REGIONS
    }

    initial_image_data = region_to_api['ROW-en'][-1]
    assert initial_image_data.url is not None
    image_content = requests.get(initial_image_data.url).content

    if not dev:
        print('Generating GitHub initial image...')
        gen_github_initial_image(image_content)

        print('Generating website initial image...')
        gen_website_initial_image(image_content)

        print('Generating API endpoints...')
        gen_api_endpoints(region_to_api)

    print('Updating website HTML...')
    update_website_html(initial_image_data)

    print('Adding headers...')
    add_headers()


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--dev', action='store_true', help='Fast dev build (skip webp/svg and non-year JSON endpoints).')
    return p.parse_args(argv)


if __name__ == '__main__':
    args = _parse_args(sys.argv[1:])
    build_website(dev=args.dev)
