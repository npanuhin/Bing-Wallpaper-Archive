import json
import os

from utils import mkpath


class Region:
    def __init__(self, region):
        self.lang, self.country = map(str.lower, region.split('-'))
        self.path = mkpath(os.path.dirname(__file__), '../api', self.country.upper())
        self.api_path = mkpath(self.path, self.country.lower() + '.json')

        os.makedirs(self.path, exist_ok=True)

        self.gcloud_images_path = mkpath(self.country.upper(), 'images')

    @property
    def mkt(self):
        return f'{self.lang}-{self.country.upper()}'

    def read_api(self) -> str:
        if not os.path.exists(self.api_path):
            return []

        with open(self.api_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_api(self, api):  # TODO
        with open(self.api_path, 'w', encoding='utf-8') as file:
            json.dump(api, file, ensure_ascii=False, indent='\t')

    def __repr__(self):
        return f'Region({self.mkt})'


# ------------------------------------------------------- Regions ------------------------------------------------------

# Canada - English: en-ca | Canada - French: fr-ca | China: zh-cn | China - English: en-cn | France: fr-fr
# Germany: de-de | India: en-in | Japan: ja-jp | United Kingdom: en-gb | United States: en-us | International: en-ww

# REGIONS = ['AU', 'CA', 'CN', 'DE', 'FR', 'IN', 'JP', 'ES', 'GB', 'US']
# REGIONS = ['en-CA', 'fr-CA', 'zh-CN', 'en-CN', 'fr-FR', 'de-DE', 'en-IN', 'ja-JP', 'en-GB', 'en-US']
REGIONS = ['en-US']

REGIONS = list(map(Region, REGIONS))
