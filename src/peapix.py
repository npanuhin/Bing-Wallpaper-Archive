#                                    ┌───────────────────────────────────────────┐
#                                    │    Copyright (c) 2022 Nikita Paniukhin    │
#                                    │      Licensed under the MIT license       │
#                                    └───────────────────────────────────────────┘
#
# ======================================================================================================================

from urllib.parse import urlsplit, urlunsplit
from traceback import print_exc
from bs4 import BeautifulSoup
import requests
import datetime
import os

from utils import mkpath, create_folder_if_absent, clear_folder, FileDownloader
from utils import Threads, _pass, add_months, prettify_data_string, SafeJson, remove_metadata

API_PATH = mkpath("../", "api")

DOWNLOADER = FileDownloader()
safe_json = SafeJson()

# ======================================================================================================================


FLAG_NOTOCH, FLAG_LATEST, FLAG_UPDATE = None, None, None


def parse_month_page(region, year, month, image_pages):
    soup = BeautifulSoup(requests.get("https://peapix.com/bing/{}/{}/{}".format(region.lower(), year, month)).text, "lxml")

    for image_block in soup.findAll("div", class_="image-list__container"):
        day = int(image_block.find("div", class_="image-list__stats").text.strip().split()[1])
        url = image_block.find("a", class_="image-list__picture-link").get('href')

        date = datetime.date(year=year, month=month, day=day).strftime("%Y-%m-%d")

        image_pages.add((date, url))


def get_image_pages(region):
    image_pages = set()

    def parseYear(year):
        print("Parsing year {}...".format(year))

        months = sorted(
            int(os.path.basename(os.path.normpath(url)))
            for url in map(
                lambda x: x.get("href"),
                BeautifulSoup(requests.get("https://peapix.com/bing/{}/{}/".format(region.lower(), year)).text, "lxml").findAll("a")
            )
            if url and url.startswith("/bing/{}/{}/".format(region.lower(), year))
        )

        for month in months:
            parse_month_page(region, year, month, image_pages)

            # break

    print("Parsing years...")
    years = sorted(
        int(os.path.basename(os.path.normpath(url)))
        for url in map(
            lambda x: x.get("href"),
            BeautifulSoup(requests.get("https://peapix.com/bing/{}/".format(region.lower())).text, "lxml").findAll("a")
        )
        if url and url.startswith("/bing/{}/".format(region.lower()))
    )

    with Threads() as threads:
        for year in years:
            threads.add(parseYear, (year, )).start()
            # break

    return image_pages


def update_latest_image_pages(image_pages, region):
    print("Updateting latest image pages...")

    latest_date = datetime.datetime.strptime(max(image_pages, key=lambda x: x[0])[0], "%Y-%m-%d").date()
    parse_month_page(region, int(latest_date.strftime("%Y")), int(latest_date.strftime("%m")), image_pages)

    last_image_pages_size = 0

    while last_image_pages_size != len(image_pages):
        last_image_pages_size = len(image_pages)
        latest_date = add_months(latest_date, 1)

        parse_month_page(region, int(latest_date.strftime("%Y")), int(latest_date.strftime("%m")), image_pages)
        # print(sorted(image_pages))


def handle_image_page(api_by_date, region, image_date, image_page_url, image_action=FLAG_NOTOCH):
    print("Starting new thread: {}".format(image_page_url))

    image_page = BeautifulSoup(requests.get("https://peapix.com" + image_page_url).text, "lxml")

    image_link = urlunsplit(list(urlsplit(
        image_page.find("div", id="download-modal").find("a", class_="btn").get("href")
    )[:3]) + [None] * 2)

    description = image_page.find("div", class_="gallery-picture").find("div", class_="row")
    title = prettify_data_string(description.find("h1", class_="typography-title").text)

    description = description.find("div", class_="picture-desc")
    copyright = prettify_data_string(description.find("p", class_="text-gray").text)

    subtitle = description.find("h3")

    description = prettify_data_string("\n".join(paragraph.text.strip() for paragraph in subtitle.find_next_siblings("p")))

    subtitle = prettify_data_string(subtitle.text)

    # Workarounds:
    if description in (title, subtitle, copyright):
        description = ""

    if subtitle == title:
        subtitle = ""

    # Constructing image date
    # date = datetime.datetime.strptime(image_page.find('time').get('datetime'), "%Y-%m-%d").strftime("%Y-%m-%d")
    date = image_page.find('time').get('datetime')

    image_path = mkpath(region, "images", date + os.path.splitext(image_link)[1])

    image = {
        "title": title if title else None,
        "subtitle": subtitle if subtitle else None,
        "copyright": copyright if copyright else None,
        "date": date,
        "description": description if description else None,
        "path": image_path
    }

    if image_action == FLAG_UPDATE or (image_action == FLAG_LATEST or not os.path.isfile(mkpath(API_PATH, image_path))):
        DOWNLOADER.download(image_link, mkpath(API_PATH, image_path))
        remove_metadata(mkpath(API_PATH, image_path))

    print(image)

    api_by_date[date] = image

    safe_json.dump(
        mkpath(API_PATH, region, region.lower() + ".json"),
        sorted(api_by_date.values(), key=lambda image: image["date"]),
        allow_cache=True,
        prettify=True,
        ensure_ascii=False
    )

    print("Thread finished")


def update(region, days_action=FLAG_NOTOCH, api_action=FLAG_NOTOCH, image_action=FLAG_NOTOCH):
    print("Starting update {{days_action={}, api_action={}, image_action={}}} for {}".format(days_action, api_action, image_action, region))

    # ================================= CREATING API, FOLDERS AND FILES =================================

    # Checking main region's api folder
    create_folder_if_absent(mkpath(API_PATH, region))
    # Checking cache folder
    create_folder_if_absent(mkpath(API_PATH, region, "images"))

    region_api_data_path = mkpath(API_PATH, region, region.lower() + ".json")

    # Checking region's api data
    if os.path.isfile(region_api_data_path):
        api = safe_json.load(region_api_data_path)
    else:
        api = []
        safe_json.dump(region_api_data_path, api, prettify=True, ensure_ascii=False)

    # Checking region's image folder
    create_folder_if_absent(mkpath(API_PATH, region, "images"))

    # =========================================== DAYS CACHE ============================================

    # Checking region cache
    if days_action <= FLAG_LATEST and os.path.isfile(mkpath("cache", ".peapix.{}.cache".format(region.lower()))):
        print("Trying to use cached api data: {}".format(region_api_data_path))

        try:
            image_pages = set(map(tuple, safe_json.load(mkpath("cache", ".peapix.{}.cache".format(region.lower())))))
            if days_action >= FLAG_LATEST:
                update_latest_image_pages(image_pages, region)
        except Exception as e:
            print("Failed to use cached api data:", e, sep=' ')
            print_exc()
            image_pages = get_image_pages(region)

    else:
        image_pages = get_image_pages(region)

    image_pages = sorted(image_pages)

    safe_json.dump(mkpath("cache", ".peapix.{}.cache".format(region.lower())), image_pages, ensure_ascii=False)
    # safe_json.dump(mkpath("cache", ".peapix.{}.cache".format(region.lower())), image_pages, prettify=True, ensure_ascii=False)

    # =================================================================================================================

    print("Found {} images".format(len(image_pages)))

    api_by_date = {image["date"]: image for image in sorted(api, key=lambda image: image["date"])}

    with Threads() as threads:
        for image_date, image_link in image_pages:

            if api_action == FLAG_NOTOCH:
                continue
            elif api_action == FLAG_LATEST:
                if image_date in api_by_date and (image_action == FLAG_NOTOCH or os.path.isfile(mkpath(API_PATH, api_by_date[image_date]["path"]))):
                    continue
            elif api_action == FLAG_UPDATE:
                pass

            try:
                t = threads.add(
                    handle_image_page,
                    (api_by_date, region, image_date, image_link, image_action)
                )
                threads.wait_free(30)
                t.start()

            except Exception:
                print_exc()

    safe_json.dump(
        mkpath(API_PATH, region, region.lower() + ".json"),
        sorted(api_by_date.values(), key=lambda image: image["date"]),
        prettify=True,
        ensure_ascii=False
    )

    print()


def updateRegions(regions, days_action=FLAG_NOTOCH, api_action=FLAG_NOTOCH, image_action=FLAG_NOTOCH):
    for region in regions:
        # clear_folder(mkpath(API_PATH, region, "images"))
        _pass(clear_folder)
        update(
            region,
            days_action=days_action,
            api_action=api_action,
            image_action=image_action
        )


# Actions:
FLAG_NOTOCH = 0  # FLAG_NOTOCH - Do not touch
FLAG_LATEST = 1  # FLAG_LATEST - Update latest (or missing images)
FLAG_UPDATE = 2  # FLAG_UPDATE - Update all


if __name__ == "__main__":
    updateRegions(
        # ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"],
        ["US"],
        days_action=FLAG_LATEST,
        api_action=FLAG_LATEST,
        image_action=FLAG_LATEST
    )
