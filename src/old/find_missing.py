from datetime import datetime, timedelta
from sys import path as sys_path
import json
import os

sys_path.append("../")
from utils import mkpath


REGION = "US"
region_path = mkpath("../../api", REGION.upper())
images_path = mkpath(region_path, "images")
START_DATE = datetime.strptime(os.path.splitext(os.listdir(images_path)[0])[0], "%Y-%m-%d").date()
END_DATE = datetime.today().date() - timedelta(days=1)  # yesterday


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


print("Searching api from {} to {}..".format(START_DATE, END_DATE))
with open(mkpath(region_path, REGION.lower() + ".json"), 'r', encoding="utf-8") as file:
    api = json.load(file)
api = set(item["date"] for item in api)

for cur_date in daterange(START_DATE, END_DATE):  # [START_DATE; END_DATE)
    if cur_date.strftime("%Y-%m-%d") not in api:
        print("Api for {} not found".format(cur_date))


print("Searching images from {} to {}..".format(START_DATE, END_DATE))
for cur_date in daterange(START_DATE, END_DATE):  # [START_DATE; END_DATE)
    if not os.path.isfile(mkpath(images_path, cur_date.strftime("%Y-%m-%d") + ".jpg")):
        print("Image for {} not found".format(cur_date))
