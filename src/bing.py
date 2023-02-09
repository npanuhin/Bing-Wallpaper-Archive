from utils import mkpath, remove_metadata
from os import makedirs, path as os_path
from requests import get as req_get
from datetime import datetime
import json

from postprocess import postprocess_api


# REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]
# REGIONS = ["en-ca", "fr-ca", "zh-cn", "en-cn", "fr-fr", "de-de", "en-in", "ja-jp", "en-gb", "en-us", "en-ww"]
REGIONS = ["en-US"]

API_PATH = mkpath("../", "api")

FORCE_SAME_DATA = True

# ======================================================================================================================


def update_api(api, new_image_api):
    date = new_image_api["date"]
    if date not in api:
        api[date] = new_image_api
        return

    for key, value in new_image_api.items():
        if FORCE_SAME_DATA and key in api[date] and api[date][key] is not None:
            assert api[date][key] == new_image_api[key], \
                'key "{}" is different for {}: "{}" vs "{}"'.format(key, date, api[date][key], new_image_api[key])

        api[date][key] = new_image_api[key]


def update(region):
    print("Updating {}...".format(region))

    makedirs(mkpath(API_PATH, "US", "images"), exist_ok=True)

    country = region[region.rfind('-') + 1:]
    with open(mkpath(API_PATH, country.upper(), country.lower() + ".json"), 'r', encoding="utf-8") as file:
        api = json.load(file)

    api = {item["date"]: item for item in api}

    # ================= https://www.bing.com/HPImageArchive.aspx =================
    print("Getting caption and image from bing.com/HPImageArchive.aspx...")

    data = req_get(
        "https://www.bing.com/HPImageArchive.aspx",
        params={"format": "js", "idx": 0, "n": 10, "mkt": region}
    ).json()["images"]

    for image_data in data:
        date = datetime.strptime(image_data["startdate"], '%Y%m%d').strftime('%Y-%m-%d')

        path = mkpath("US", "images", date + ".jpg")

        # Downloading image
        if not os_path.isfile(mkpath(API_PATH, path)):
            with open(mkpath(API_PATH, path), 'wb') as file:
                file.write(req_get("https://bing.com" + image_data["urlbase"] + "_UHD.jpg").content)
            remove_metadata(mkpath(API_PATH, path))

        update_api(api, {
            "caption": image_data["title"],
            "date": date,
            "path": path
        })

    # ====================== https://www.bing.com/hp/api/model ======================
    print("Getting title, caption and copyright from bing.com/hp/api/model...")
    data = req_get("https://www.bing.com/hp/api/model", cookies={"_UR": "cdxOff=1", "_EDGE_S": "mkt=en-US"}).json()["MediaContents"]

    for image_data in data:
        date = datetime.strptime(image_data["Ssd"][:image_data["Ssd"].find('_')], '%Y%m%d').strftime('%Y-%m-%d')

        image_data = image_data["ImageContent"]

        update_api(api, {
            "title": image_data["Title"],
            "caption": image_data["Headline"],
            "copyright": image_data["Copyright"],
            "date": date
        })

    # ================= https://www.bing.com/hp/api/v1/imagegallery =================
    print("Getting everyting else from bing.com/hp/api/v1/imagegallery...")
    data = req_get(
        "https://www.bing.com/hp/api/v1/imagegallery",
        params={"format": "json", "mkt": region}
    ).json()["data"]["images"]

    for image_data in data:
        date = datetime.strptime(image_data["isoDate"], '%Y%m%d').strftime('%Y-%m-%d')

        description = image_data["description"]
        i = 2
        while "descriptionPara" + str(i) in image_data and image_data["descriptionPara" + str(i)]:
            description += '\n' + image_data["descriptionPara" + str(i)]
            i += 1

        description = description.replace("  ", " ")  # Fix for double spaces

        update_api(api, {
            "title": image_data["title"],
            "subtitle": image_data["caption"],
            "copyright": image_data["copyright"],
            "description": description,
            "date": date
        })

    with open(mkpath(API_PATH, country.upper(), country.lower() + ".json"), 'w', encoding="utf-8") as file:
        json.dump(postprocess_api(list(api.values())), file, ensure_ascii=False, indent=4)


def update_all(*args, **kwargs):
    for region in REGIONS:
        update(region, *args, **kwargs)


if __name__ == "__main__":
    update_all()
