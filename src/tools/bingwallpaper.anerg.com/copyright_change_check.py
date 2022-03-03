from fuzzywuzzy import fuzz

from sys import path as sys_path
sys_path.append("../../")

from utils import mkpath, SafeJson


API_PATH = mkpath("../../../api")
REGION = "US"
safe_json = SafeJson()


old_api = safe_json.load(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".json"))
new_api = safe_json.load(REGION.lower() + ".new.json")
# new_api = safe_json.load(REGION.lower() + ".new.patched.json")

assert len(old_api) == len(new_api)

for i in range(len(new_api)):
    old_item = old_api[i]
    new_item = new_api[i]

    old_copyright = old_item["copyright"]
    new_copyright = new_item["copyright"]

    if old_copyright == new_copyright:
        continue

    if old_copyright is None:
        continue

    # if old_copyright == new_copyright[:-1]:
    #     continue

    # if old_copyright.endswith(") ©") and old_copyright[:-len(") ©")] == new_copyright:
    #     continue

    if fuzz.partial_ratio(new_copyright.lower(), old_copyright.lower()) < 100:
        print('Warning! Low partial ration for new copyright: "{}" -> "{}" ({})'.format(
            old_copyright, new_copyright, new_item["date"]
        ))

    # if new_item["date"] in (
    #     "2010-02-23"
    # ):
    #     continue

    # print('"{}"\t->\t"{}"\t("{}" | {})'.format(old_copyright, new_copyright, new_item["title"], new_item["date"]))
    # inp = input("1 - old, 2 - new, 3 - custom: ").strip()

    # if inp == '1':
    #     new_api[i]["copyright"] = old_copyright
    # elif inp == '2':
    #     new_api[i]["copyright"] = new_copyright
    # else:
    #     new_api[i]["copyright"] = inp

    # safe_json.dump(mkpath(API_PATH, REGION.upper(), REGION.lower() + ".patched.json"), new_api, prettify=True)
