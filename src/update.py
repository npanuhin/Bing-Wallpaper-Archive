import re

from bing import update_all
from Region import Region


# ----------------------------------------------- Update api and images ------------------------------------------------

update_all()

print('Update finished\n')

# --------------------------------------------- Fetch last image in en-US ----------------------------------------------

us_api = Region('en-US').read_api()

latest_image = max(us_api, key=lambda item: item['date'])

print(f'Last US image: {latest_image["date"]}')

# --------------------------------------------------- Update README ----------------------------------------------------

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
