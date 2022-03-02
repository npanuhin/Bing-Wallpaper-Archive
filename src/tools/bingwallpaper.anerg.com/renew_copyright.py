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

for cur_month in month_year_iter(date(2020, 1, 1), date(2022, 4, 1)):
    cur_month = date(*cur_month, 1)
    cur_month_str = cur_month.strftime("%Y-%m")

    print("Parsing {}...".format(cur_month.strftime("%Y%m")))
    soup = BeautifulSoup(req_get("https://bingwallpaper.anerg.com/us/" + cur_month.strftime("%Y%m")).text, "lxml")
    soup = soup.find("body").find("div", id="jssor_1")

    # with open("subpage.html", 'w', encoding="utf-8") as file:
    #     file.write(soup.prettify())

    for image in soup.find_all("img", {"data-u": "image"}):
        title = image.parent.parent.find("div", class_="intro").text
        # image_url = image.get("src")
        # print("https:" + image_url)

        # title = title.rstrip("(Bing United States)")

        if title.endswith("(Bing United States)"):
            title = title[:-len("(Bing United States)")]

        # if '(' in title and ')' in title:

        copyright = title[title.rfind('(') + 1:title.rfind(')')]

        assert len(copyright) > 0 and len(copyright) != len(title), "Can not find copyright in {}".format(title)

        title = title[:title.rfind('(')].strip()

        print((title, copyright))

        print("Searching {}...".format(title))
        search_result = None
        for seach_length in range(1, len(title) + 1):
            seach_count = 0

            for index, item in enumerate(api):
                if item["date"].startswith(cur_month_str) and item["title"].startswith(title[:seach_length]):
                    seach_count += 1
                    search_result = index

                    print(item["title"], title)
                    print(len(item["title"]), len(title))

                    if len(item["title"]) == len(title):
                        seach_count = 1
                        break

            if seach_count <= 1:
                break

            print()

        print(seach_count, seach_length)

        assert seach_count == 1, "Title not found: {}".format(title)

        # print(search_result, api[search_result]["copyright"], copyright)

        api[search_result]["copyright"] = copyright

        # print(search_result, api[search_result]["copyright"], copyright)

    # break

safe_json.dump(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".new.json"), api, prettify=True)
