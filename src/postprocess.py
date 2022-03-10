from json import load as json_load, dump as json_dump

from utils import mkpath


def postproces_item(api_data):
    if api_data["caption"] == api_data["subtitle"]:
        api_data["caption"] = None

    return api_data


def postprocess_api(api):
    for i, item in enumerate(api):
        api[i] = postproces_item(item)

    return api


def postproces_api_file(file_path, *json_args, **json_kwargs):
    with open(mkpath(file_path), 'r', encoding="utf-8") as file:
        api = json_load(file)

    api = postprocess_api(api)

    with open(mkpath(file_path), 'w', encoding="utf-8") as file:
        json_dump(api, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    postproces_api_file(mkpath("../api/US/us.json"), ensure_ascii=False, indent=4)
