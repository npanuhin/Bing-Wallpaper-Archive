import json
import os

from utils import mkpath


class Region:
    def __init__(self, region: str):
        self.lang, self.country = map(str.lower, region.split('-'))
        self.path = mkpath(os.path.dirname(__file__), '../api', self.country.upper())
        self.api_path = mkpath(self.path, self.lang.lower() + '.json')

        os.makedirs(self.path, exist_ok=True)

    @property
    def mkt(self):
        return f'{self.lang}-{self.country.upper()}'

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

    def __repr__(self):
        return f'Region({self.mkt})'


# ------------------------------------------------------- Regions ------------------------------------------------------

# Canada - English: en-CA | Canada - French: fr-CA | China: zh-CN | China - English: en-CN | France: fr-FR
# Germany: de-DE | India: en-IN | Japan: ja-JP | United Kingdom: en-GB | United States: en-US | International: en-WW (?)
# Spain: es-ES

# Update times:
# GB: 0:00 UTC
# CA: 5:00 UTC
# US: 8:00 UTC
# CN: 16:00 UTC
# JP: 15:00 UTC
# IN: 18:30 UTC
# DE: 23:00 UTC
# FR: 23:00 UTC
# ES: 23:00 UTC

# REGIONS = ['AU', 'CA', 'CN', 'DE', 'FR', 'IN', 'JP', 'ES', 'GB', 'US']
# REGIONS = ['en-CA', 'fr-CA', 'zh-CN', 'en-CN', 'fr-FR', 'de-DE', 'en-IN', 'ja-JP', 'en-GB', 'en-US']
REGIONS = ['en-US']

REGIONS = list(map(Region, REGIONS))
