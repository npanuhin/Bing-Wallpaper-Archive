from dataclasses import dataclass, asdict
import datetime

# -------------------------------------------------------- Api ---------------------------------------------------------

@dataclass(kw_only=True, frozen=True)
class ApiEntry:
    title: str | None = None
    caption: str | None = None
    subtitle: str | None = None
    copyright: str | None = None
    description: str | None = None
    date: datetime.date
    bing_url: str | None = None
    url: str | None = None  # TODO

type Api = list[ApiEntry]

DATE_FORMAT = '%Y-%m-%d'

# ------------------------------------------------------- Regions ------------------------------------------------------
# See src/scripts/get_regions.py for more information

# _REGIONS = ['en-US']
_REGIONS = [
    'pt-BR',
    'en-CA',
    'fr-CA',
    'fr-FR',
    'de-DE',
    'en-IN',
    'it-IT',
    'ja-JP',
    'zh-CN',
    'es-ES',
    'en-GB',
    'en-US'
]

_ROW = 'ROW'


if __name__ == '__main__':
    print(asdict(ApiEntry(
        date=datetime.date(2024, 1, 1),
        url='some_url'
    )))
