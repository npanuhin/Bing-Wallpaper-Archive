from datetime import datetime
import json
import re

from bing import update_all, REGIONS
from Region import Region


WEBSITE_START_DATE = '2017-05-10'


# ------------------------------------------------ Update api and images -----------------------------------------------

update_all()

print('Update finished\n')

# ----------------------------------------------- Fetch last image in US -----------------------------------------------

us_api = Region('en-US').read_api()

latest_image = max(us_api, key=lambda item: item['date'])

print(f'Last US image: {latest_image["date"]}')

# ---------------------------------------------------- Update README ---------------------------------------------------

with open('../README.md', 'r', encoding='utf-8') as file:
    readme = file.read()

readme = re.sub(
    r'<a id="last_image_link" href=".*?">',
    f'<a id="last_image_link" href="{latest_image["url"]}">',
    readme
)

readme = re.sub(
    r'<img id="last_image" title=".*?" alt=".*?" src=".*?">',
    f'<img id="last_image" title="{latest_image["title"]}" alt="{latest_image["title"]}" src="{latest_image["url"]}">',
    readme
)

readme = re.sub(
    r'<img id="last_image_badge" alt=".*?" src=".*?">',
    f'<img id="last_image_badge" alt="Last image: {latest_image["date"]}" src='
    f'"https://img.shields.io/badge/Last_image-{latest_image["date"].replace("-", "--")}-informational?style=flat">',
    readme
)

with open('../README.md', 'w', encoding='utf-8') as file:
    file.write(readme)

# ------------------------------------------------- Update website api -------------------------------------------------

for region in REGIONS:
    api = region.read_api()

    api_for_website = {
        datetime.strptime(item['date'], '%Y-%m-%d').strftime('%Y%m%d'): item['title']
        for item in api
        if item['date'] >= WEBSITE_START_DATE
    }

    with open(f'website/api/{region.country}.json', 'w', encoding='utf-8') as file:
        json.dump(api_for_website, file, ensure_ascii=False, separators=(',', ':'))

    print(f'Updated website api for {region.country.upper()}')
