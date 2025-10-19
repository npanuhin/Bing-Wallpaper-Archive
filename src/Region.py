from urllib.parse import urlparse, parse_qs
import json
import os
import re

from utils import API_HOME, mkpath


type ApiEntry = dict[str, str | None]
type Api = list[ApiEntry]


RE_FLAGS = re.IGNORECASE | re.VERBOSE


class Market:
    def __init__(self, mkt: str):
        if mkt == 'ROW':
            self.api_lang = 'en'
            self.api_country = 'ROW'
        else:
            lang, country = mkt.split('-')
            self.api_lang = lang.lower()
            self.api_country = country.upper()

        self.lang = self.api_lang
        self.country = 'RU' if self.api_country == 'ROW' else self.api_country

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

        self.path = mkpath(API_HOME, self.api_country)
        self.api_path = mkpath(self.path, self.api_lang + '.json')

        os.makedirs(self.path, exist_ok=True)

    def read_api(self, path: str | None = None) -> Api:
        if path is None:
            path = self.api_path

        if not os.path.exists(path):
            return []

        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_api(self, api: Api, output_path: str | None = None, *args, **kwargs):
        if output_path is None:
            output_path = self.api_path

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        kwargs = {
            'ensure_ascii': False,
            'indent': '\t',
        } | kwargs

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(api, file, *args, **kwargs)


def extract_mkt(url: str) -> Market | None:
    # https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg
    name = parse_qs(urlparse(url).query)['id'][0]

    match = re.fullmatch(r'OHR\..+_(\D+)\d+.*', name, RE_FLAGS)
    return None if match is None else Market(match.group(1))


# ------------------------------------------------------- Regions ------------------------------------------------------
# See src/scripts/get_regions.py for more information

# REGIONS = ['en-US']
REGIONS = [
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

ROW = Region('ROW')

REGIONS = [ROW] + list(map(Region, REGIONS))

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
