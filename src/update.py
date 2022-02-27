from json import load as json_load, dump as json_dump
from datetime import datetime
from bing import update_all
from utils import mkpath
import re


# REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]
# en-WW
REGIONS = ["en-US"]

website_start_date = "2017-05-10"


# =============================================== Update api and images ================================================

update_all(
    # days_action=FLAG_LATEST,
    # api_action=FLAG_LATEST,
    # # image_action=FLAG_LATEST
    # image_action=FLAG_NOTOUCH
)

with open(mkpath("../", "api", "US", "us.json"), 'r', encoding="utf-8") as file:
    us_api = json_load(file)

latest_image_date = us_api[-1]["date"]
print("Updated US to", latest_image_date)

# =================================================== Update README ====================================================

with open(mkpath("../", "README.md"), 'r+', encoding="utf-8") as file:
    readme = file.read()
    file.seek(0)
    readme = re.sub(
        r"<img alt=\"Last image:.*?\" src=\".+?\">",
        '<img alt="Last image: {}" src="https://img.shields.io/static/v1?label=Last%20image&message={}&color=informational&style=flat">'.format(
            latest_image_date, latest_image_date
        ),
        readme
    )
    readme = re.sub(
        r"!\[\]\(api/US/images/.+\)",
        "![](api/US/images/{}.jpg)".format(latest_image_date),
        readme
    )
    file.write(readme)
    file.truncate()

# ================================================= Update website api =================================================

for region in REGIONS:
    country = region[region.rfind('-') + 1:]
    with open(mkpath("../", "api", country, country.lower() + ".json"), 'r', encoding="utf-8") as file:
        api = json_load(file)

    api_for_website = {
        datetime.strptime(item["date"], '%Y-%m-%d').strftime('%Y%m%d'): item['title']
        for item in api if item["date"] >= website_start_date
    }

    with open(mkpath("website", "api", country.lower() + ".json"), 'w', encoding="utf-8") as file:
        json_dump(api_for_website, file, ensure_ascii=False, separators=(',', ':'))
