from urllib.parse import urlparse, parse_qs
import os
import re

from structures import ApiEntry, _REGIONS, _ROW

from system_utils import API_PATH, mkpath
import api


class Market:
    def __init__(self, market_id: str):
        if market_id == 'ROW':
            self.lang = self.api_lang = 'en'
            self.api_country = 'ROW'
            self.country = 'RU'
        else:
            lang, country = market_id.split('-')
            self.lang = self.api_lang = lang.lower()
            self.country = self.api_country = country.upper()

    def __str__(self):
        return f'{self.lang}-{self.api_country}'

    def __repr__(self):
        if self.api_country == 'ROW':
            return f'ROW [{self.lang}-{self.country}]'
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Market) and self.lang == other.lang and self.country == other.country


class Region(Market):
    def __init__(self, market_id: str):
        super().__init__(market_id)

        self.root_path = mkpath(API_PATH, self.api_country)
        self.api_path = mkpath(self.root_path, self.api_lang + '.json')

        os.makedirs(self.root_path, exist_ok=True)

    def read_api(self) -> list[ApiEntry]:
        return api.read_api(self.api_path)

    def write_api(self, api_data: list[ApiEntry], output_path: str | None = None, minify: bool = False):
        api.write_api(api_data, output_path or self.api_path, minify=minify)


def extract_market_from_url(url: str) -> Market | None:
    # https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg
    name = parse_qs(urlparse(url).query)['id'][0]

    match = re.fullmatch(r'OHR\..+_(\D+)\d+.*', name, re.IGNORECASE | re.VERBOSE)
    return None if match is None else Market(match.group(1))


ROW = Region(_ROW)
REGIONS = [ROW] + list(map(Region, _REGIONS))
