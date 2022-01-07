from peapix import updateRegions, FLAG_LATEST
from utils import mkpath
import os
import re


updateRegions(
    # ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"],
    ["US"],
    days_action=FLAG_LATEST,
    api_action=FLAG_LATEST,
    image_action=FLAG_LATEST
)

latest_image_date = os.path.splitext(os.listdir(mkpath("../", "api", "US", "images"))[-1])[0]
print("Updated US to", latest_image_date)


with open(mkpath("../", "README.md"), 'r', encoding="utf-8") as file:
    readme = file.read()

readme = re.sub(
    r'<img alt="Last image: (\d+-\d+-\d+)" src="https:\/\/img\.shields\.io\/static\/v1\?label=Last%20image,%20US&message=(\d+-\d+-\d+)&color=informational&style=flat">',
    '<img alt="Last image: {}" src="https://img.shields.io/static/v1?label=Last%20image,%20US&message={}&color=informational&style=flat">'.format(latest_image_date, latest_image_date),
    readme
)

with open(mkpath("../", "README.md"), 'w', encoding="utf-8") as file:
    file.write(readme)
