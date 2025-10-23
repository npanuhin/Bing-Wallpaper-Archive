import re

from bing import update_all
from Region import ROW

# ----------------------------------------------- Update api and images ------------------------------------------------

update_all()

print('Update finished\n')

# --------------------------------------------- Fetch last image in en-US ----------------------------------------------

latest_image = ROW.read_api()[-1]

print(f'Last ROW image: {latest_image.date}')

# --------------------------------------------------- Update README ----------------------------------------------------

with open('../README.md', 'r', encoding='utf-8') as file:
    readme = file.read()

readme = re.sub(
    r'<a id="last_image_link" href=".*?">',
    f'<a id="last_image_link" href="{latest_image.url}">',
    readme
)

# readme = re.sub(
#     r'<img id="last_image" title=".*?" alt=".*?" src=".*?">',
#     f'<img id="last_image" title="{latest_image.title}" alt="{latest_image.title}" src="{latest_image.url}">',
#     readme
# )

# badge_formatted_date = latest_image.date.strftime(DATE_FORMAT).replace("-", "--")
# readme = re.sub(
#     r'<img id="last_image_badge" alt=".*?" src=".*?">',
#     f'<img id="last_image_badge" alt="Last image: {latest_image.date}" src='
#     f'"https://img.shields.io/badge/Last_image-{badge_formatted_date}-informational?style=flat">',
#     readme
# )

with open('../README.md', 'w', encoding='utf-8') as file:
    file.write(readme)
