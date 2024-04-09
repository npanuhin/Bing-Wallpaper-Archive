from datetime import datetime, timedelta
import os

import requests

from Region import ApiEntry, REGIONS, Region, extract_mkt
from postprocess import postprocess_api
from cloudflare import CloudflareR2
from utils import mkpath, posixpath


storage = CloudflareR2()

# ======================================================================================================================


def extract_base_url(image_url: str) -> str:
    # '/th?id=OHR.MountainDayChina_EN-US0394775210_1920x1080.webp'
    if '_1920x1080' in image_url:
        return image_url.split('_1920x1080')[0]
    if '_UHD' in image_url:
        return image_url.split('_UHD')[0]
    raise ValueError(f'Can not extract base url from {image_url}')


def get_uhd_url(region: Region, base_url: str) -> str:
    # '/th?id=OHR.MountainDayChina_EN-US0394775210_UHD.jpg'
    url = f'https://bing.com{base_url}_UHD.jpg'
    market = extract_mkt(url)
    assert market == region, f'Region mismatch: {market}, but should be {region}'
    return url


def parse_date(date_string: str) -> datetime.date:
    for fmt in ('%Y%m%d_%H%M', '%Y%m%d%H%M', '%Y%m%d'):
        try:
            parsed = datetime.strptime(date_string, fmt)
        except ValueError:
            continue

        # Add one day if time is after 15:00
        return parsed.date() + timedelta(days=int(parsed.hour >= 15))


def compare_values(key: str, old_value: str | None, new_value: str) -> str:
    if old_value is None:
        return new_value

    if old_value == new_value:
        return old_value

    if key == 'description':
        if len(new_value) < len(old_value):
            assert old_value.startswith(new_value), f'\n"{old_value}"\nvs\n"{new_value}"'
            return old_value
        else:
            assert new_value.startswith(old_value)
            print(f'Rewriting description: {len(old_value)} -> {len(new_value)}')
            return new_value

    if key in ('title', 'caption'):
        new_value = new_value.replace('’', "'")
        if old_value == new_value:
            return old_value

    raise ValueError(f'key "{key}" is different:\n"{old_value}"\nvs\n"{new_value}"')


def update_api(api_by_date: dict[str, ApiEntry], new_image_api: ApiEntry):
    date = new_image_api['date']
    item = api_by_date.get(date)
    if item is None:
        api_by_date[date] = new_image_api
        return

    for key, new_value in new_image_api.items():
        item[key] = compare_values(key, item.get(key), new_value)


def update(region: Region):
    print(f'Updating {repr(region)}...')

    common_params = {'mkt': region, 'setlang': region.lang, 'cc': region.country}

    api_by_date = {item['date']: item for item in region.read_api()}

    to_download = set()

    # ------------------------------------------------------------------------------------------------------------------
    # https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=100&mkt=en-US&setlang=en&cc=US
    print('Getting caption, image and image url from bing.com/HPImageArchive.aspx...')
    # TODO: extract title and copyright

    data = requests.get(
        'https://www.bing.com/HPImageArchive.aspx',
        params={'format': 'js', 'idx': 0, 'n': 10} | common_params
    ).json()['images']

    for image_data in data:
        date = parse_date(image_data['fullstartdate']).strftime('%Y-%m-%d')

        image_url = get_uhd_url(region, image_data['urlbase'])
        to_download.add(date)

        update_api(api_by_date, {
            'date': date,
            'caption': image_data['title'],
            'bing_url': image_url
        })

    # ------------------------------------------------------------------------------------------------------------------
    # https://www.bing.com/hp/api/model?mkt=en-US&setlang=en&cc=US
    print('Getting title, caption, copyright, description and image url from bing.com/hp/api/model...')

    data = requests.get(
        'https://www.bing.com/hp/api/model',
        params=common_params
    ).json()['MediaContents']

    for image_data in data:
        date = parse_date(image_data['Ssd']).strftime('%Y-%m-%d')

        image_data = image_data['ImageContent']
        image_url = get_uhd_url(region, extract_base_url(image_data['Image']['Url']))
        to_download.add(date)

        description = image_data['Description']
        description = description.replace('  ', ' ')  # Fix for double spaces

        update_api(api_by_date, {
            'date': date,
            'title': image_data['Title'],
            'caption': image_data['Headline'],
            'copyright': image_data['Copyright'],
            'description': description,
            'bing_url': image_url
        })

    # ------------------------------------------------------------------------------------------------------------------
    # https://www.bing.com/hp/api/v1/imagegallery?format=json&mkt=en-US&setlang=en&cc=US
    print('Getting title, subtitle, copyright, description and image url from bing.com/hp/api/v1/imagegallery...')
    data = requests.get(
        'https://www.bing.com/hp/api/v1/imagegallery',
        params={'format': 'json'} | common_params
    ).json()['data']['images']

    for image_data in data:
        date = parse_date(image_data['isoDate']).strftime('%Y-%m-%d')

        description = image_data['description']
        i = 2
        while image_data.get(f'descriptionPara{i}'):
            description += '\n' + image_data[f'descriptionPara{i}']
            i += 1
        description = description.replace('  ', ' ')  # Fix for double spaces

        image_url = get_uhd_url(region, extract_base_url(image_data['imageUrls']['landscape']['ultraHighDef']))
        to_download.add(date)

        update_api(api_by_date, {
            'date': date,
            'title': image_data['title'],
            'subtitle': image_data['caption'],
            'copyright': image_data['copyright'],
            'description': description,
            'bing_url': image_url
        })

    # ------------------------------------------------------------------------------------------------------------------
    print('Downloading images and uploading to Storage...')

    os.makedirs('_temp', exist_ok=True)

    for date in sorted(to_download):
        filename = date + '.jpg'
        image_path = mkpath('_temp', filename)

        with open(image_path, 'wb') as file:
            file.write(requests.get(api_by_date[date]['bing_url']).content)

        api_by_date[date]['url'] = storage.upload_file(
            image_path,
            posixpath(mkpath(region.api_country.upper(), region.api_lang.lower(), filename)),
            skip_exists=True
        )

        os.remove(image_path)

    os.rmdir('_temp')

    # ------------------------------------------------------------------------------------------------------------------

    region.write_api(
        postprocess_api(list(api_by_date.values()))
    )
    print()


def update_all():
    for region in REGIONS:
        update(region)


if __name__ == '__main__':
    update_all()
