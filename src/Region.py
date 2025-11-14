from urllib.parse import urlparse, parse_qs
from dataclasses import asdict
import datetime
import json
import os
import re

from structures import ApiEntry, _REGIONS, _ROW, DATE_FORMAT

from utils import API_PATH, mkpath


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
        return f'{self.lang}-{self.country}'

    def __repr__(self):
        if self.api_country == 'ROW':
            return f'ROW [{self}]'
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
        if not os.path.isfile(self.api_path):
            return []

        with open(self.api_path, 'r', encoding='utf-8') as file:
            return [
                ApiEntry(
                    **parsed_json | {
                        'date': datetime.datetime.strptime(parsed_json['date'], DATE_FORMAT).date()
                    }
                )
                for parsed_json in json.load(file)
            ]

    def write_api(self, api: list[ApiEntry], output_path: str | None = None, minify: bool = False):
        if output_path is None:
            output_path = self.api_path

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(
                [asdict(entry) for entry in api],
                file,
                ensure_ascii=False,
                indent=None if minify else '\t',
                separators=(',', ':') if minify else None,
                default=lambda item: item.isoformat() if isinstance(item, datetime.date) else item,
            )


def extract_market_from_url(url: str) -> Market | None:
    # https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg
    name = parse_qs(urlparse(url).query)['id'][0]

    match = re.fullmatch(r'OHR\..+_(\D+)\d+.*', name, re.IGNORECASE | re.VERBOSE)
    return None if match is None else Market(match.group(1))


ROW = Region(_ROW)
REGIONS = [ROW] + list(map(Region, _REGIONS))

if __name__ == '__main__':
    assert extract_market_from_url(
        'https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg'
    ) == Market('en-US')
    assert extract_market_from_url(
        'https://bing.com/th?id=OHR.WhiteEyes_ROW2172958331_1920x1200.jpg&rf=LaDigue_1920x1200.jpg'
    ) == Market('ROW')

    assert str(Region('ROW')) == 'en-RU'
    assert str(Region('en-US')) == 'en-US'

    assert repr(Region('ROW')) == 'ROW [en-RU]'
    assert repr(Region('en-US')) == 'en-US'
