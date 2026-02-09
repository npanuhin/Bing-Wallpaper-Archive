from Region import Region, extract_market_from_url


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
