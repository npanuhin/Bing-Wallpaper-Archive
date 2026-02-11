import datetime
import math
import os
import re

from system_utils import mkpath, WEBSITE_ROOT
from Region import ROW, REGIONS
from cloudflare import CloudflareR2

LATEST_IMAGE = ROW.read_api()[-1]
print(f'Last ROW image: {LATEST_IMAGE.date}')


# --------------------------------------------------- Update README ----------------------------------------------------

def update_html_attribute(text, tag_id, attr, value):
    pattern = rf'(id="{tag_id}" [^>]*?{attr}=").*?(")'
    return re.sub(pattern, rf'\1{value}\2', text)


def update_html_text(text, tag_id, value):
    pattern = rf'(<(?P<tag>[^\s>]+)[^>]*id="{tag_id}"[^>]*>).*?(</(?P=tag)>)'
    return re.sub(pattern, rf'\1{value}\3', text, flags=re.DOTALL)


def format_size_value(size_mb: float) -> str:
    if size_mb > 10:
        digits = 0
    elif size_mb > 1:
        digits = 1
    else:
        digits = 2

    factor = 10 ** digits
    v = math.ceil(size_mb * factor) / factor

    s = f'{v:.{digits}f}'
    if digits > 0:
        s = s.rstrip('0').rstrip('.')
    return s


def format_endpoint_size(size_bytes, can_increase=False):
    size_mb = size_bytes / (1024 * 1024)
    val = format_size_value(size_mb)

    digits_count = sum(c.isdigit() for c in val)
    has_dot = '.' in val

    res = val
    if not has_dot:
        res = '\xa0' + res

    missing_digits = max(0, 3 - digits_count)
    if missing_digits > 0:
        res = ('\u2002' * missing_digits) + res

    res += '\xa0MB\xa0'
    res += '↑' if can_increase else '\xa0'

    return res


def get_avg_size(filename_pattern):
    normal_sizes = []
    min_sizes = []

    if not os.path.isdir(WEBSITE_ROOT):
        raise FileNotFoundError(f'Website root directory not found: {WEBSITE_ROOT}')

    for f in os.listdir(WEBSITE_ROOT):
        if not os.path.isfile(mkpath(WEBSITE_ROOT, f)):
            continue
        if re.fullmatch(filename_pattern, f):
            size = os.path.getsize(mkpath(WEBSITE_ROOT, f))
            if '.min.' in f:
                min_sizes.append(size)
            else:
                normal_sizes.append(size)

    avg_normal = sum(normal_sizes) / len(normal_sizes) if normal_sizes else 0
    avg_min = sum(min_sizes) / len(min_sizes) if min_sizes else 0

    return avg_normal, avg_min


def format_endpoint_size_cell(size_bytes, size_bytes_min, can_increase=False):
    s1 = format_endpoint_size(size_bytes, can_increase)
    # s2 = format_endpoint_size(size_bytes_min, can_increase)
    # return f'\n        {s1}\n        <br>\n        {s2}\n      '
    return f'\n        {s1}\n      '


def update_readme():
    with open('../README.md', 'r', encoding='utf-8') as file:
        readme = file.read()

    # Update last image info
    readme = update_html_attribute(readme, 'last_image_link', 'href', LATEST_IMAGE.url)
    readme = update_html_attribute(readme, 'last_image', 'title', LATEST_IMAGE.title)
    readme = update_html_attribute(readme, 'last_image', 'alt', LATEST_IMAGE.title)

    # badge_date = LATEST_IMAGE.date.strftime('%Y-%m-%d')
    # badge_formatted_date = badge_date.replace("-", "--")
    # badge_url = f"https://img.shields.io/badge/Last_image-{badge_formatted_date}-informational?style=flat"
    #
    # readme = update_html_attribute(readme, 'last_image_badge', 'alt', f"Last image: {badge_date}")
    # readme = update_html_attribute(readme, 'last_image_badge', 'src', badge_url)

    # Update sizes
    size_all, size_all_min = get_avg_size(r'all\.json')
    readme = update_html_text(readme, 'endpoint_everything_size',
                              format_endpoint_size_cell(size_all, size_all_min, can_increase=True))

    size_country, size_country_min = get_avg_size(r'[A-Z]{2}-[a-z]{2}\.json')
    readme = update_html_text(readme, 'endpoint_country_size',
                              format_endpoint_size_cell(size_country, size_country_min, can_increase=True))

    size_year, size_year_min = get_avg_size(r'[A-Z]{2}-[a-z]{2}\.\d{4}\.json')
    readme = update_html_text(readme, 'endpoint_year_size',
                              format_endpoint_size_cell(size_year, size_year_min, can_increase=False))

    size_month, size_month_min = get_avg_size(r'[A-Z]{2}-[a-z]{2}\.\d{4}\.\d{2}\.json')
    readme = update_html_text(readme, 'endpoint_month_size',
                              format_endpoint_size_cell(size_month, size_month_min, can_increase=False))

    # Update image size (approximate)
    storage = CloudflareR2()

    current_year = datetime.date.today().year
    years_to_check = [current_year, current_year - 1]

    total_image_size = 0
    image_count = 0

    print(f'Calculating average image size for years: {years_to_check}...')
    for region in REGIONS:
        for year in years_to_check:
            prefix = f'{region.api_country}/{region.api_lang}/{year}-'
            size, count = storage.get_stats(prefix)
            total_image_size += size
            image_count += count

    if image_count == 0:
        # Fallback to total usage if no recent images found (e.g. beginning of year or error)
        usage = storage.get_bucket_usage()
        total_image_size, image_count = usage or (0, 0)
        print('Using total bucket usage as fallback')

    print(f'Total recent images size: {format_endpoint_size(total_image_size)}')
    print(f'Recent images count: {image_count}')
    size_image = total_image_size / image_count if image_count > 0 else 0
    print(f'Average recent file size: {format_endpoint_size(size_image)}')

    readme = update_html_text(readme, 'endpoint_image_size',
                              f'<b>{format_endpoint_size(size_image, can_increase=False)}</b>')

    with open('../README.md', 'w', encoding='utf-8') as file:
        file.write(readme)

    print('README updated')


if __name__ == '__main__':
    update_readme()
