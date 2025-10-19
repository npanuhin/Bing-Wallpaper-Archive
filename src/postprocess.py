from structures import Api, ApiEntry
from Region import REGIONS


def postproces_item(entry: ApiEntry) -> ApiEntry:
    # Alert duplication of `caption` and `subtitle`
    # if entry.caption is not None and entry.caption == entry.subtitle:
    #     print(f'caption == subtitle for {entry.date}')

    return entry


def postprocess_api(api: Api) -> Api:
    for i, item in enumerate(api):
        api[i] = postproces_item(item)

    api.sort(key=lambda entry: entry.date)

    return api


if __name__ == '__main__':
    for region in REGIONS:
        print(f'Postprocessing {region}...')
        region.write_api(
            postprocess_api(region.read_api())
        )
        print()
