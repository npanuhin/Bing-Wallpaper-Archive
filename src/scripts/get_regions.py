import sys

import requests
from bs4 import BeautifulSoup

sys.path.append('../')
from Region import REGIONS, Market, extract_market_from_url
from system_utils import warn


# All regions list:
# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/market-codes


# Active regions from online source 1:
# Canada - English: en-CA | Canada - French: fr-CA | China: zh-CN | China - English: en-CN | France: fr-FR
# Germany: de-DE | India: en-IN | Japan: ja-JP | United Kingdom: en-GB | United States: en-US | International: en-WW (?)
# Spain: es-ES

# Active regions from online source 2:
# `de-DE`, `en-CA`, `en-GB`, `en-IN`, `en-US`, `es-ES`, `fr-CA`, `fr-FR`, `it-IT`, `ja-JP`, `ko-KR` (sometimes),
# `pt-BR` and `zh-CN`

# + ROW

# Update times:
# GB: 0:00 UTC
# CA: 5:00 UTC
# US: 8:00 UTC
# CN: 16:00 UTC
# JP: 15:00 UTC
# IN: 18:30 UTC
# DE: 23:00 UTC
# FR: 23:00 UTC
# ES: 23:00 UTC

# Final check:
# en-CA (Canada)  - yes
# fr-CA           - yes
# zh-CN (China)   - yes
# en-CN           - no
# fr-FR (France)  - yes
# de-DE (Germany) - yes
# en-IN (India)   - yes
# ja-JP (Japan)   - yes
# en-GB (UK)      - yes
# en-US (US)      - yes
# es-ES (Spain)   - yes
# it-IT (Italy)   - yes
# ko-KR           - no (sometimes?)
# pt-BR (Brazil)  - yes

# ROW (International | "Rest Of the World") - yes [will use "en-RU" for now, with assert to "ROW" URL]


# Brute-force checking all regions from the market list:

def get_regions() -> set[Market]:
    page = requests.get('https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/market-codes')
    assert page.status_code == 200

    soup = BeautifulSoup(page.text, 'html.parser')

    # with open('page.html', 'w', encoding='utf-8') as file:
    #     file.write(soup.prettify())

    markets = list(map(Market, (
        item.text.strip() for item in soup.select('div.content table tbody tr td:nth-child(3)')
    )))

    result = {Market('ROW')}
    for market in markets:
        data = requests.get(
            'https://www.bing.com/HPImageArchive.aspx',
            params={'mkt': str(market), 'setlang': market.lang, 'cc': market.country, 'format': 'js', 'idx': 0, 'n': 10}
        ).json()['images']

        for image in data:
            url = 'https://bing.com' + image['urlbase']
            print(market, url)

            extracted = extract_market_from_url(url)
            if extracted is not None:
                result.add(extracted)

    return result


def check_regions() -> bool:
    regions = get_regions()
    print(sorted(map(str, regions)))  # Can be copied to src/Region.py and website's HTML/JS
    print()

    if regions == set(REGIONS):
        print('✅ Regions are up-to-date')
        return True

    warn('Regions are outdated. Please update src/Region.py')
    print('Old regions:', sorted(map(str, REGIONS)))
    print('New regions:', sorted(map(str, regions)))
    return False


if __name__ == '__main__':
    if not check_regions():
        sys.exit(1)
