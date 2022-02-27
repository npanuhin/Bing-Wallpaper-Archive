import sys
sys.path.append("../")

from utils import mkpath, SafeJson


API_PATH = mkpath("../../api")

safe_json = SafeJson()

REGIONS = ["en-US"]


for region in REGIONS:
    country = region[region.rfind('-') + 1:]
    api = safe_json.load(mkpath(API_PATH, country.upper(), country.lower() + ".new.json"))

    # Separate subtitle into quote and subtitle (buy ".")
    for item in api:

        if "quote" in item and item["quote"] is not None:
            continue

        if item["subtitle"] is not None:
            if item["subtitle"].count('.') == 1:
                item["quote"] = item["subtitle"][:item["subtitle"].find('.')].strip()
                item["subtitle"] = item["subtitle"][item["subtitle"].find('.') + 1:].strip()

            elif item["subtitle"].count('.') > 1:
                print(item["subtitle"])

    # Rearrange keys
    for i in range(len(api)):
        api[i] = {
            key: (api[i][key] if key in api[i] else None)
            for key in ("title", "subtitle", "quote", "copyright", "description", "date", "path")  # Outdated!
        }

    safe_json.dump(mkpath(API_PATH, country.upper(), country.lower() + ".new.json"), api, prettify=True)
