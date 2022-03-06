from sys import path as sys_path
sys_path.append("../")

from datetime import date, datetime, timedelta
from utils import mkpath, SafeJson
import os


API_PATH = mkpath("../../api")
REGION = "US"
START_DATE = date(2010, 1, 1)
END_DATE = datetime.today().date()


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


print("Searching api from {} to {}..".format(START_DATE, END_DATE))
api = SafeJson().load(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".json"))
api = set(item["date"] for item in api)

for cur_date in daterange(START_DATE, END_DATE):  # [START_DATE; END_DATE)
    if cur_date.strftime("%Y-%m-%d") not in api:
        print("Api for {} not found".format(cur_date))


print("Searching images from {} to {}..".format(START_DATE, END_DATE))
for cur_date in daterange(START_DATE, END_DATE):  # [START_DATE; END_DATE)
    if not os.path.isfile(mkpath(API_PATH, REGION.upper(), "images", cur_date.strftime("%Y-%m-%d") + ".jpg")):
        print("Image for {} not found".format(cur_date))
