from json import load as json_load, dump as json_dump
from urllib.parse import urlencode
from datetime import datetime
from bing import update_all
import os
import re

from utils import mkpath


# REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]
# en-WW
REGIONS = ["en-US"]

API_PATH = "../api"

website_start_date = "2017-05-10"


# =============================================== Update api and images ================================================

update_all()

latest_image_date = os.path.splitext(max(os.listdir(mkpath(API_PATH, "US", "images"))))[0]
print("Updated US to", latest_image_date)

# =================================================== Update README ====================================================

with open(mkpath("../README.md"), 'r', encoding="utf-8") as file:
    readme = file.read()

shields_io_badge = "https://img.shields.io/static/v1?" + urlencode({
    "label": "Last image",
    "message": latest_image_date,
    "color": "informational",
    "style": "flat"
})
readme = re.sub(
    r"<img alt=\"Last image:.*?\" src=\".+?\">",
    f'<img alt="Last image: {latest_image_date}" src="{shields_io_badge}">',
    readme
)
readme = re.sub(
    r"(\[!\[\]\(api/US/images/)(.+)(\.jpg\)]\(https://github\.com/npanuhin/bing-wallpaper-archive/blob/master/api/US/images/)\2(.jpg\?raw=true\))",
    fr"\g<1>{latest_image_date}\g<3>{latest_image_date}\g<4>",
    readme
)

with open(mkpath("../README.md"), 'w', encoding="utf-8") as file:
    file.write(readme)

# ================================================= Update website api =================================================

for region in REGIONS:
    country = region.split('-')[1]
    with open(mkpath("../api", country, country.lower() + ".json"), 'r', encoding="utf-8") as file:
        api = json_load(file)

    api_for_website = {
        datetime.strptime(item["date"], '%Y-%m-%d').strftime('%Y%m%d'): item['title']
        for item in api if item["date"] >= website_start_date
    }

    with open(mkpath("website/api", country.lower() + ".json"), 'w', encoding="utf-8") as file:
        json_dump(api_for_website, file, ensure_ascii=False, separators=(',', ':'))
