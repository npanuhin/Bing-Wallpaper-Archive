import re
from urllib.parse import parse_qs, urlparse

from Region import Region, extract_market_from_url


def extract_base_url(image_url: str) -> str:
    # '/th?id=OHR.MountainDayChina_EN-US0394775210_1920x1080.webp'
    if '_1920x1080' in image_url:
        return image_url.split('_1920x1080')[0]
    if '_UHD' in image_url:
        return image_url.split('_UHD')[0]
    raise ValueError(f'Cannot extract base url from {image_url}')


def extract_image_slug(image_url: str) -> str | None:
    # 'https://bing.com/th?id=OHR.PondCypress_ES-ES1413599118_UHD.jpg' -> 'OHR.PondCypress_ES-ES'
    parsed = urlparse(image_url)
    qs = parse_qs(parsed.query)
    name = qs.get('id', [parsed.path.split('/')[-1]])[0]
    match = re.match(r'(OHR\.[^_]+_[a-zA-Z-]+?)\d+', name)
    return match.group(1) if match else None


def get_uhd_url(region: Region, base_url: str) -> str:
    # '/th?id=OHR.MountainDayChina_EN-US0394775210_UHD.jpg'
    url = f'https://bing.com{base_url}_UHD.jpg'
    market = extract_market_from_url(url)
    if market != region:
        raise ValueError(f'Region mismatch: {market}, but should be {region}')
    return url
