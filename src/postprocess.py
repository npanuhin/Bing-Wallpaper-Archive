from Region import Api, ApiEntry, REGIONS, Region


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


def postproces_item(image_api: ApiEntry) -> ApiEntry:
    # Put fields in the correct order and fill blanks
    image_api = {
        key: (image_api[key] if key in image_api else None)
        for key in FIELD_ORDER
    }

    # Alert duplication of `caption` and `subtitle`
    if image_api['caption'] is not None and image_api['caption'] == image_api['subtitle']:
        # image_api['caption'] = None
        # print(image_api)
        print(f'caption == subtitle for {image_api["date"]}')
        # raise AssertionError(f'caption == subtitle for {image_api["date"]}')

    return image_api


def postprocess_api(api: Api) -> Api:
    for i, item in enumerate(api):
        api[i] = postproces_item(item)

    api.sort(key=lambda image_api: image_api['date'])

    return api


def postproces_region(region: Region):
    print(f'Postprocessing {region}...')
    region.write_api(postprocess_api(region.read_api()))


if __name__ == '__main__':
    for region in REGIONS:
        postproces_region(region)
        print()
