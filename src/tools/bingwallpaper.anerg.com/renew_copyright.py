from requests import get as req_get
from bs4 import BeautifulSoup
from datetime import date  # , timedelta
# from copy import deepcopy

from sys import path as sys_path
sys_path.append("../../")

from utils import mkpath, SafeJson

API_PATH = mkpath("../../../api")
REGION = "US"
safe_json = SafeJson()


def month_year_iter(start_date, end_date):  # [start_date:end_date)
    start_year, start_month = start_date.year, start_date.month
    end_year, end_month = end_date.year, end_date.month

    ym_start = 12 * start_year + start_month - 1
    ym_end = 12 * end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m + 1


api = safe_json.load(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".json"))
# api = {item["date"]: item for item in api}
# new_api = deepcopy(api)

# soup = BeautifulSoup(
#     req_get("https://bingwallpaper.anerg.com/us").text,
#     "lxml"
# )

# with open("page.html", 'w', encoding="utf-8") as file:
#     file.write(soup.prettify())

with open("page.html", 'r', encoding="utf-8") as file:
    soup = BeautifulSoup(file.read(), "lxml")

for cur_date in month_year_iter(date(2022, 3, 1), date(2022, 4, 1)):
    cur_date = date(*cur_date, 1)
    print("Parsing {}...".format(cur_date.strftime("%Y%m")))
    soup = BeautifulSoup(req_get("https://bingwallpaper.anerg.com/us/" + cur_date.strftime("%Y%m")).text, "lxml")

    soup = soup.find("body").find("div", id="jssor_1")

    with open("subpage.html", 'w', encoding="utf-8") as file:
        file.write(soup.prettify())

    images = soup.find_all("img", {"data-u": "image"})

    for image in images:
        title = image.parent.parent.find("div", class_="intro").text
        # image_url = image.get("src")
        # print("https:" + image_url)

        # title = title.rstrip("(Bing United States)")

        if title.endswith("(Bing United States)"):
            title = title[:-len("(Bing United States)")]

        copyright = title[title.rfind('(') + 1:title.rfind(')')]

        assert len(copyright) > 0, "Can not find copyright in {}".format(title)

        title = title[:title.rfind('(')].strip()

        # print(copyright)
        # print(title)

        print("Searching {}...".format(title))
        seach_length, seach_count, search_result = 0, len(api), None
        while seach_count > 1:
            seach_length += 1
            seach_count = 0

            for index, item in enumerate(api):
                if item["title"][:seach_length] == title[:seach_length]:
                    seach_count += 1
                    search_result = index

        assert seach_count == 1, "Title not found: {}".format(title)

        # print(search_result, api[search_result]["copyright"], copyright)

        api[search_result]["copyright"] = copyright

        # print(search_result, api[search_result]["copyright"], copyright)

    break

safe_json.dump(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".new.json"), api, prettify=True)
