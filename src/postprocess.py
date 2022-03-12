from json import load as json_load, dump as json_dump

from utils import mkpath

FIELDS = ("title", "caption", "subtitle", "copyright", "description", "date", "path")


def postproces_item(image_api):
    image_api = {
        key: (image_api[key] if key in image_api else None)
        for key in FIELDS
    }

    if image_api["caption"] == image_api["subtitle"]:
        image_api["caption"] = None

    return image_api


def postprocess_api(api):
    for i, item in enumerate(api):
        api[i] = postproces_item(item)

    api.sort(key=lambda image_api: image_api["date"])

    return api


def postproces_api_file(file_path, *json_args, **json_kwargs):
    with open(mkpath(file_path), 'r', encoding="utf-8") as file:
        api = json_load(file)

    api = postprocess_api(api)

    with open(mkpath(file_path), 'w', encoding="utf-8") as file:
        json_dump(api, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    postproces_api_file(mkpath("../api/US/us.json"), ensure_ascii=False, indent=4)
