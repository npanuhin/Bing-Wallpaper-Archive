from typing import Callable

from Region import REGIONS
from structures import Api, ApiEntry


class ApiPostprocessor:
    def __init__(self):
        self.item_processors: list[Callable[[ApiEntry], ApiEntry]] = []
        self.api_processors: list[Callable[[Api], Api]] = []

    def item_processor(self, func: Callable[[ApiEntry], ApiEntry]):
        self.item_processors.append(func)
        return func

    def api_processor(self, func: Callable[[Api], Api]):
        self.api_processors.append(func)
        return func

    def process_item(self, entry: ApiEntry) -> ApiEntry:
        for processor in self.item_processors:
            entry = processor(entry)
        return entry

    def process_api(self, api: Api) -> Api:
        for i, item in enumerate(api):
            api[i] = self.process_item(item)

        for processor in self.api_processors:
            api = processor(api)

        return api


postprocessor = ApiPostprocessor()


# @postprocessor.item_processor
# def replace_nbsp_with_space(entry: ApiEntry) -> ApiEntry:
#     fields_to_fix = ['title', 'caption', 'subtitle', 'copyright', 'description']
#     changes = {}
#     for field_name in fields_to_fix:
#         if hasattr(entry, field_name):
#             text = getattr(entry, field_name)
#             if text and isinstance(text, str):
#                 # NBSP: \u00A0, NNBSP: \u202F
#                 fixed_text = text.replace('\u00A0', ' ').replace('\u202F', ' ')
#                 if fixed_text != text:
#                     changes[field_name] = fixed_text
#
#     if changes:
#         return replace(entry, **changes)
#     return entry


@postprocessor.api_processor
def sort_by_date(api: Api) -> Api:
    api.sort(key=lambda entry: entry.date)
    return api


if __name__ == '__main__':
    for region in REGIONS:
        print(f'Postprocessing {region}...')
        region.write_api(
            postprocessor.process_api(region.read_api())
        )
