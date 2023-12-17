from Region import Region


FIELD_ORDER = (
    'title',
    'caption',
    'subtitle',
    'copyright',
    'description',
    'date',
    'bing_url',
    'url'
)


def postproces_item(image_api: dict) -> dict:
    # Put fields in the correct order and fill blanks
    image_api = {
        key: (image_api[key] if key in image_api else None)
        for key in FIELD_ORDER
    }

    # Alert duplication of `caption` and `subtitle`
    if image_api['caption'] is not None and image_api['caption'] == image_api['subtitle']:
        # image_api['caption'] = None
        raise AssertionError(f'caption == subtitle for {image_api["date"]}')

    return image_api


def postprocess_api(api: list[dict]) -> list[dict]:
    for i, item in enumerate(api):
        api[i] = postproces_item(item)

    api.sort(key=lambda image_api: image_api['date'])

    return api


def postproces_region(region: Region):
    print(f'Postprocessing {region}...')
    api = region.read_api()
    region.write_api(postprocess_api(api))


if __name__ == '__main__':
    postproces_region(Region('en-US'))
