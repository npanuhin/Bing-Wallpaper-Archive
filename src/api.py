from dataclasses import asdict
import datetime
import json
import os

from structures import ApiEntry, DATE_FORMAT


def write_json(data, path: str, minify: bool = False):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=None if minify else '\t',
            separators=(',', ':') if minify else None,
            default=lambda item: item.isoformat() if isinstance(item, (datetime.date, datetime.datetime)) else item,
        )


def read_api(api_path: str) -> list[ApiEntry]:
    if not os.path.isfile(api_path):
        return []

    with open(api_path, 'r', encoding='utf-8') as file:
        return [
            ApiEntry(
                **parsed_json | {
                    'date': datetime.datetime.strptime(parsed_json['date'], DATE_FORMAT).date()
                }
            )
            for parsed_json in json.load(file)
        ]


def write_api(api: list[ApiEntry], output_path: str, minify: bool = False):
    write_json(
        [asdict(entry) for entry in api],
        output_path,
        minify=minify
    )
