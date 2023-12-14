import json
import os

from utils import mkpath


class Region:
    API_HOME = '../api'

    def __init__(self, region):
        self.lang, self.country = map(str.lower, region.split('-'))
        self.path = mkpath(Region.API_HOME, self.country.upper())
        self.api_path = mkpath(self.path, self.country.lower() + '.json')
        self.images_path = mkpath(self.path, 'images')

        os.makedirs(self.images_path, exist_ok=True)

        self.relative_path = self.country.upper()
        self.relative_images_path = mkpath(self.relative_path, 'images')

    @property
    def mkt(self):
        return f'{self.lang}-{self.country.upper()}'

    def read_api(self) -> str:
        with open(self.api_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_api(self, api):  # TODO
        with open(self.api_path, 'w', encoding='utf-8') as file:
            json.dump(api, file, ensure_ascii=False, indent=4)

    def __repr__(self):
        return f'Region({self.mkt})'
