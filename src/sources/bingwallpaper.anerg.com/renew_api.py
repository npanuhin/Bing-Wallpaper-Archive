from requests import get as req_get
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from datetime import date
import os
import re

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

cur_api_pos = 0
for cur_month in month_year_iter(date(2010, 1, 1), date(2022, 3, 1)):
    cur_month = date(*cur_month, 1)
    cur_month_str = cur_month.strftime("%Y-%m")
    cur_month_short_str = cur_month.strftime("%Y%m")

    print("Parsing {}...".format(cur_month_short_str))
    cached = False
    if os.path.exists(mkpath("cache", cur_month_short_str + ".html")):
        with open(mkpath("cache", cur_month_short_str + ".html"), 'r', encoding="utf-8") as file:
            html = file.read()
            if html:
                soup = BeautifulSoup(html, "lxml")
                cached = True

    if not cached:
        soup = BeautifulSoup(req_get("https://bingwallpaper.anerg.com/us/" + cur_month_short_str).text, "lxml")

        with open(mkpath("cache", cur_month_short_str + ".html"), 'w', encoding="utf-8") as file:
            file.write(str(soup))

    soup = soup.find("body").find("div", id="jssor_1")

    # with open("subpage.html", 'w', encoding="utf-8") as file:
    #     file.write(soup.prettify())

    images = soup.find_all("img", {"data-u": "image"})
    for image_index, image in enumerate(images):
        title = image.parent.parent.find("div", class_="intro").text.strip()

        # image_url = image.get("src")
        # print("https:" + image_url)

        if title.endswith("(Bing United States)"):
            title = title[:-len("(Bing United States)")].strip()

        title = title.replace("\\'", "'").replace('\\"', '"').replace("  ", " ").replace(" ", " ")

        match1 = re.match(
            r"^(.+?)\s*\(\s*(©[^\)]+?)\s*\)?\s*(?:\s*©)?$",
            title, re.IGNORECASE
        )
        match2 = re.match(
            r"^(.+?)(?:\s*\-\-\s*)(?!.+(?:\s*\-\-\s*))(.+)$",
            title, re.IGNORECASE
        )
        match3 = re.match(
            r"^(.+?)(?:\s+by\s+|\s*\–\s*|\s+\-\s*|\s*\-\s+)(?!.+(?:\s+by\s+|\s*\–\s*|\s+\-\s*|\s*\-\s+))(.+)$",
            title, re.IGNORECASE
        )
        match4 = re.match(
            r"^(.+?)\s*\(\s*([^\)]+?)\s*\)?\s*(?:\s*©)?$",
            title, re.IGNORECASE
        )
        match5 = re.match(
            r"^(.+?)\s*\(\s*(.+?)\s*\)\s*(?:\s*©)?$",
            title, re.IGNORECASE
        )

        if not match1 and not match2 and match3 and (match4 or match5):
            print("Multiple matches on \"{}\"".format(title))

        if match1:
            match = match1
        elif match2:
            match = match2
        elif match3:
            match = match3
        elif match4:
            match = match4
        elif match5:
            match = match5
        else:
            print("Title not parsed: \"{}\" from {}".format(title, cur_month_str))
            continue

        title, copyright = match.groups()
        # print((title, copyright))

        assert title and copyright, "Title or copyright is empty: ({}, {})".format(title, copyright)

        # title = title.replace("  ", " ")
        # copyright = copyright.replace("  ", " ")

        search_title = title
        if title == "The Copper River Delta in Chugach National Forest, Alaska":
            search_title = "The Copper River Delta in Wrangell-St. Elias National Park and Preserve, Alaska"

        api_index = max(
            range(max(0, cur_api_pos - 5), min(len(api), cur_api_pos + 7)),
            key=lambda i: fuzz.partial_ratio(search_title.lower(), api[i]["title"].lower())  # partial_ratio, token_sort_ratio, WRatio
        )
        if fuzz.partial_ratio(search_title, api[api_index]["title"]) >= 80:
            pass
        else:
            if image_index == len(images) - 1:
                continue
            print("Can not find title{}: (\"{}\", \"{}\") for month {}".format(
                " (last day of month)" if image_index == len(images) - 1 else "",
                search_title, copyright, cur_month_str
            ))
            print("Ratios:", [
                fuzz.partial_ratio(search_title, api[i]["title"]) for i in range(cur_api_pos - 5, cur_api_pos + 7)
            ])
            continue

        cur_api_pos = api_index

        # print(search_result, api[search_result]["copyright"], copyright)
        # print((copyright.lower(), api[cur_api_pos]["copyright"].lower()))

        if api[cur_api_pos]["copyright"] is not None and \
                fuzz.partial_ratio(copyright.lower(), api[cur_api_pos]["copyright"].lower()) < 95:
            print('Warning! Low partial ration for new copyright: "{}" -> "{}" ({})'.format(
                api[cur_api_pos]["copyright"], copyright, cur_month_str
            ))

        if api[cur_api_pos]["title"] is not None and \
                fuzz.partial_ratio(title.lower(), api[cur_api_pos]["title"].lower()) < 95:
            print('Warning! Low partial ration for new title: "{}" -> "{}" ({})'.format(
                api[cur_api_pos]["title"], title, cur_month_str
            ))

        api[cur_api_pos]["title"] = title
        api[cur_api_pos]["copyright"] = copyright

    # break

safe_json.dump(REGION.lower() + ".new.json", api, prettify=True)
