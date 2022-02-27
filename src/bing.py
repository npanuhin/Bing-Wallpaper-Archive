from utils import mkpath, SafeJson, remove_metadata
from requests import get as req_get
from datetime import datetime
from os import makedirs


# REGIONS = ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"]
# REGIONS = ["en-ca", "fr-ca", "zh-cn", "en-cn", "fr-fr", "de-de", "en-in", "ja-jp", "en-gb", "en-us", "en-ww"]
REGIONS = ["en-US"]

API_PATH = mkpath("../", "api")

safe_json = SafeJson()

# ======================================================================================================================


def update(region):
    print("Updating {}...".format(region))

    makedirs(mkpath(API_PATH, "US", "images"), exist_ok=True)

    country = region[region.rfind('-') + 1:]
    api = safe_json.load(mkpath(API_PATH, country.upper(), country.lower() + ".json"))

    api = {item["date"]: item for item in api}

    # ================= https://www.bing.com/HPImageArchive.aspx =================
    print("Getting subtitle...")

    data = req_get(
        "https://www.bing.com/HPImageArchive.aspx",
        params={"format": "js", "idx": 0, "n": 100, "mkt": region}
    ).json()["images"]

    for cur_data in data:
        date = datetime.strptime(cur_data["startdate"], '%Y%m%d').strftime('%Y-%m-%d')

        new_api = {
            "subtitle": cur_data["title"],
            "date": date
        }

        if date in api:
            api[date].update(new_api)
        else:
            api[date] = new_api

    # ================= https://www.bing.com/hp/api/v1/imagegallery =================
    print("Getting other info...")
    data = req_get(
        "https://www.bing.com/hp/api/v1/imagegallery",
        params={"format": "json", "mkt": region}
    ).json()["data"]["images"]

    for cur_data in data:
        date = datetime.strptime(cur_data["isoDate"], '%Y%m%d').strftime('%Y-%m-%d')

        path = mkpath("US", "images", date + ".jpg")

        with open(mkpath(API_PATH, path), 'wb') as file:
            file.write(req_get("https://bing.com" + cur_data["imageUrls"]["landscape"]["ultraHighDef"]).content)
        remove_metadata(mkpath(API_PATH, path))

        description = cur_data["description"]
        i = 2
        while "descriptionPara" + str(i) in cur_data and cur_data["descriptionPara" + str(i)]:
            description += '\n' + cur_data["descriptionPara" + str(i)]
            i += 1

        description = description.replace("  ", " ")  # Fix for double spaces

        new_api = {
            "title": cur_data["title"],
            "caption": cur_data["caption"],
            "copyright": cur_data["copyright"][:-1],  # TODO: Needs a fix!
            "description": description,
            "date": date,
            "path": path
        }

        if date in api:
            api[date].update(new_api)
        else:
            api[date] = new_api

    safe_json.dump(
        mkpath(API_PATH, country.upper(), country.lower() + ".json"),
        [
            {
                key: (image[key] if key in image else None)
                for key in (
                    ("title", "caption", "subtitle", "copyright", "description", "date", "path")
                )
            }
            for image in sorted(api.values(), key=lambda item: item["date"])
        ],
        prettify=True
    )


def update_all(*args, **kwargs):
    for region in REGIONS:
        update(region, *args, **kwargs)


if __name__ == "__main__":
    update_all()
