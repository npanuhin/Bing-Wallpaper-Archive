from urllib.parse import urlparse, parse_qs
import json
import os
import re

from utils import mkpath


RE_FLAGS = re.IGNORECASE | re.VERBOSE


class Market:
    def __init__(self, region: str):
        if region == 'ROW':
            self.api_lang = self.lang = 'en'
            self.api_country = 'ROW'
            self.country = 'RU'
        else:
            self.lang, self.country = region.split('-')
            self.lang = self.api_lang = self.lang.lower()
            self.country = self.api_country = self.country.upper()

    def __str__(self):
        return f'{self.lang}-{self.country}'

    def __repr__(self):
        if self.api_country == 'ROW':
            return f'ROW [{str(self)}]'
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Market) and self.lang == other.lang and self.country == other.country


class Region(Market):
    def __init__(self, mkt: str):
        super().__init__(mkt)

        self.path = mkpath(os.path.dirname(__file__), '../api', self.api_country)
        self.api_path = mkpath(self.path, self.api_lang + '.json')

        os.makedirs(self.path, exist_ok=True)

    def read_api(self) -> str:
        if not os.path.exists(self.api_path):
            return []

        with open(self.api_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_api(self, api: list[dict], output_path=None, *args, **kwargs):
        if output_path is None:
            output_path = self.api_path

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        kwargs = {
            'ensure_ascii': False,
            'indent': '\t',
        } | kwargs

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(api, file, *args, **kwargs)


def extract_mkt(url: str) -> Market:
    # https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg
    name = parse_qs(urlparse(url).query)['id'][0]

    match = re.fullmatch(r'OHR\..+_([^\d]+)\d+.*', name, RE_FLAGS)
    return Market(match.group(1))


# ------------------------------------------------------- Regions ------------------------------------------------------
# See src/scripts/get_regions.py for more information

# REGIONS = ['en-US']
REGIONS = [
    'ROW',
    'pt-BR',
    'en-CA',
    'fr-CA',
    'fr-FR',
    'de-DE',
    'en-IN',
    'it-IT',
    'ja-JP',
    'zh-CN',
    'es-ES',
    'en-GB',
    'en-US'
]

REGIONS = list(map(Region, REGIONS))

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    assert extract_mkt('https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg') == Market('en-US')
    assert extract_mkt(
        'https://bing.com/th?id=OHR.WhiteEyes_ROW2172958331_1920x1200.jpg&rf=LaDigue_1920x1200.jpg'
    ) == Market('ROW')

    assert str(Region('ROW')) == 'en-RU'
    assert str(Region('en-US')) == 'en-US'

    assert repr(Region('ROW')) == 'ROW [en-RU]'
    assert repr(Region('en-US')) == 'en-US'
