import dataclasses
import datetime
import os
from shutil import rmtree

import requests

from Region import REGIONS, Region, extract_market_from_url
from cloudflare import CloudflareR2
from postprocess import postprocess_api
from structures import ApiEntry, DATE_FORMAT
from utils import mkpath, posixpath, warn, fetch_json

storage = CloudflareR2()


# ======================================================================================================================


def extract_base_url(image_url: str) -> str:
    # '/th?id=OHR.MountainDayChina_EN-US0394775210_1920x1080.webp'
    if '_1920x1080' in image_url:
        return image_url.split('_1920x1080')[0]
    if '_UHD' in image_url:
        return image_url.split('_UHD')[0]
    raise ValueError(f'Cannot extract base url from {image_url}')


def get_uhd_url(region: Region, base_url: str) -> str:
    # '/th?id=OHR.MountainDayChina_EN-US0394775210_UHD.jpg'
    url = f'https://bing.com{base_url}_UHD.jpg'
    market = extract_market_from_url(url)
    assert market == region, f'Region mismatch: {market}, but should be {region}'
    return url


def parse_date(date_string: str) -> datetime.date | None:
    date_string = date_string.strip()

    if '_' in date_string:
        datetime_format = '%Y%m%d_%H%M'
        has_time = True
    elif len(date_string) == 12:
        datetime_format = '%Y%m%d%H%M'
        has_time = True
    elif len(date_string) == 8:
        datetime_format = '%Y%m%d'
        has_time = False
    else:
        warn(f'parse_date: unexpected date format: {date_string!r}')
        return None

    try:
        parsed = datetime.datetime.strptime(date_string, datetime_format)
        print(f'[Date parsing] parsed {date_string!r} with {datetime_format!r} -> {parsed}')
    except ValueError:
        warn(f'parse_date: cannot parse date string: {date_string!r}')
        return None

    if has_time and parsed.hour >= 15:
        # TODO: explain in docs
        # TODO: Check if this is correct with '%Y%m%d'
        parsed = parsed + datetime.timedelta(days=1)

    return parsed.date()


def add_entry(api_by_date: dict[datetime.date, ApiEntry], new_entry: ApiEntry) -> bool:
    """
    :return: True if the api_by_date was modified, False otherwise
    """

    date = new_entry.date

    if date not in api_by_date:
        api_by_date[date] = new_entry
        return True

    old_entry = api_by_date[date]

    if old_entry.bing_url != new_entry.bing_url:
        warn(f'Force-rewriting api for {date} due to Bing URL change:\n'
             f'"{old_entry.bing_url}" -> "{new_entry.bing_url}"')
        api_by_date[date] = new_entry
        return True

    merged_data = dataclasses.asdict(old_entry)
    new_data = dataclasses.asdict(new_entry)
    changed = False

    for key, new_value in new_data.items():
        if new_value is None:
            continue

        old_value = merged_data[key]
        if old_value is None:
            merged_data[key] = new_value
            changed = True
            continue

        if old_value == new_value:
            continue

        match key:
            case 'description':
                if old_value.startswith(new_value):
                    continue

            case 'title' | 'caption':  # TODO
                new_value = new_value.replace('’', "'")

        if old_value != new_value:
            warn(f'Rewriting key `{key}` for {date}:\n{old_value}\nvs\n{new_value}')
            merged_data[key] = new_value
            changed = True

    if changed:
        api_by_date[date] = ApiEntry(**merged_data | {'date': date})

    return changed


def update(region: Region):
    print(f'Updating {repr(region)}...')

    common_params = {'mkt': region, 'setlang': region.lang, 'cc': region.country}

    api_by_date = {item.date: item for item in region.read_api()}

    to_download = set()

    # ------------------------------------------------------------------------------------------------------------------
    # https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=100&mkt=en-US&setlang=en&cc=US
    print('Getting caption, image and image url from bing.com/HPImageArchive.aspx...')
    # TODO: extract title and copyright

    data = fetch_json(
        'https://www.bing.com/HPImageArchive.aspx',
        params=common_params | {'format': 'js', 'idx': 0, 'n': 10}
    )['images']

    for image_data in data:
        date = parse_date(image_data['fullstartdate'].strip())
        if date is None:
            warn(f'Cannot parse date:\n{image_data}')
            continue

        caption = image_data['title'].strip()
        bing_url = get_uhd_url(region, image_data['urlbase'].strip())

        new_entry = ApiEntry(
            date=date,
            caption=caption,
            bing_url=bing_url
        )
        # if add_entry(api_by_date, new_entry):
        to_download.add(date)

    # ------------------------------------------------------------------------------------------------------------------
    # https://www.bing.com/hp/api/model?mkt=en-US&setlang=en&cc=US
    print('Getting title, caption, copyright, description and image url from bing.com/hp/api/model...')

    data = fetch_json(
        'https://www.bing.com/hp/api/model',
        params=common_params
    )['MediaContents']

    for image_data in data:
        date = parse_date(image_data['Ssd'].strip())
        if date is None:
            warn(f'Cannot parse date:\n{image_data}')
            continue

        title = image_data['ImageContent']['Title'].strip()
        caption = image_data['ImageContent']['Headline'].strip()
        copyright = image_data['ImageContent']['Copyright'].strip()
        bing_url = get_uhd_url(region, extract_base_url(image_data['ImageContent']['Image']['Url'].strip()))

        description = image_data['ImageContent']['Description'].strip()
        description = description.replace('  ', ' ')  # Fix for double spaces

        new_entry = ApiEntry(
            date=date,
            title=title,
            caption=caption,
            copyright=copyright,
            description=description,
            bing_url=bing_url
        )
        # if add_entry(api_by_date, new_entry):
        to_download.add(date)

    # ------------------------------------------------------------------------------------------------------------------
    # https://www.bing.com/hp/api/v1/imagegallery?format=json&mkt=en-US&setlang=en&cc=US
    print('Getting title, subtitle, copyright, description and image url from bing.com/hp/api/v1/imagegallery...')
    data = fetch_json(
        'https://www.bing.com/hp/api/v1/imagegallery',
        params=common_params | {'format': 'json'}
    )['data']['images']

    for image_data in data:
        date = parse_date(image_data['isoDate'].strip())
        if date is None:
            warn(f'Cannot parse date:\n{image_data}')
            continue

        title = image_data['title'].strip()
        subtitle = image_data['caption'].strip()
        copyright = image_data['copyright'].strip()

        description = image_data['description'].strip()
        i = 2
        while image_data.get(f'descriptionPara{i}') is not None:
            description += '\n' + image_data[f'descriptionPara{i}'].strip()
            i += 1
        description = description.strip().replace('  ', ' ')  # Fix for double spaces

        bing_url = get_uhd_url(region, extract_base_url(image_data['imageUrls']['landscape']['ultraHighDef'].strip()))

        new_entry = ApiEntry(
            date=date,
            title=title,
            subtitle=subtitle,
            copyright=copyright,
            description=description,
            bing_url=bing_url
        )
        # if add_entry(api_by_date, new_entry):
        to_download.add(date)

    # ------------------------------------------------------------------------------------------------------------------
    print('Downloading images and uploading to Storage...')

    os.makedirs('_temp', exist_ok=True)

    for date in sorted(to_download):
        filename = date.strftime(DATE_FORMAT) + '.jpg'
        temp_image_path = mkpath('_temp', filename)

        old_entry = api_by_date[date]

        with open(temp_image_path, 'wb') as file:
            file.write(requests.get(old_entry.bing_url).content)

        new_url = storage.upload_file(
            temp_image_path,
            posixpath(mkpath(region.api_country.upper(), region.api_lang.lower(), filename)),
            skip_exists=False
        )

        new_entry = dataclasses.replace(old_entry, url=new_url)

        api_by_date[date] = new_entry

    rmtree('_temp')

    # ------------------------------------------------------------------------------------------------------------------

    region.write_api(
        postprocess_api(list(api_by_date.values()))
    )
    print()


def update_all():
    for region in REGIONS:
        update(region)


# ---------------------------------------------------- Development -----------------------------------------------------

if __name__ == '__main__':
    update_all()
