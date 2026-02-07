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

def update_html_attribute(text, tag_id, attr, value):
    pattern = rf'(id="{tag_id}" [^>]*?{attr}=").*?(")'
    return re.sub(pattern, rf'\1{value}\2', text)


with open('../README.md', 'r', encoding='utf-8') as file:
    readme = file.read()

readme = update_html_attribute(readme, 'last_image_link', 'href', latest_image.url)
readme = update_html_attribute(readme, 'last_image', 'title', latest_image.title)
readme = update_html_attribute(readme, 'last_image', 'alt', latest_image.title)

# badge_date = latest_image.date.strftime('%Y-%m-%d')
# badge_formatted_date = badge_date.replace("-", "--")
# badge_url = f"https://img.shields.io/badge/Last_image-{badge_formatted_date}-informational?style=flat"
#
# readme = update_html_attribute(readme, 'last_image_badge', 'alt', f"Last image: {badge_date}")
# readme = update_html_attribute(readme, 'last_image_badge', 'src', badge_url)

with open('../README.md', 'w', encoding='utf-8') as file:
    file.write(readme)
