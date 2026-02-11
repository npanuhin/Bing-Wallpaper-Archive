import pytest

from bing_utils import extract_base_url, get_uhd_url
from Region import Region


def test_extract_base_url():
    assert extract_base_url(
        '/th?id=OHR.MountainDayChina_EN-US0394775210_1920x1080.webp'
    ) == '/th?id=OHR.MountainDayChina_EN-US0394775210'
    assert extract_base_url(
        '/th?id=OHR.MountainDayChina_EN-US0394775210_UHD.jpg'
    ) == '/th?id=OHR.MountainDayChina_EN-US0394775210'

    with pytest.raises(ValueError):
        extract_base_url('invalid_url')


def test_get_uhd_url():
    region = Region('en-US')
    base_url = '/th?id=OHR.MountainDayChina_EN-US0394775210'

    expected_url = 'https://bing.com/th?id=OHR.MountainDayChina_EN-US0394775210_UHD.jpg'
    assert get_uhd_url(region, base_url) == expected_url


def test_get_uhd_url_mismatch():
    region = Region('en-GB')
    base_url = '/th?id=OHR.MountainDayChina_EN-US0394775210'

    with pytest.raises(ValueError):
        get_uhd_url(region, base_url)
