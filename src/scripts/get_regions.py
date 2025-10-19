import sys

from bs4 import BeautifulSoup
import requests

sys.path.append('../')
from Region import REGIONS, Market, extract_market_from_url
from utils import warn


# All regions list:
# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/market-codes


# Canada - English: en-CA | Canada - French: fr-CA | China: zh-CN | China - English: en-CN | France: fr-FR
# Germany: de-DE | India: en-IN | Japan: ja-JP | United Kingdom: en-GB | United States: en-US | International: en-WW (?)
# Spain: es-ES

# Other information:
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

def get_regions() -> list[Market]:
    page = requests.get('https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/market-codes')
    assert page.status_code == 200

    soup = BeautifulSoup(page.text, 'lxml')

    # with open('page.html', 'w', encoding='utf-8') as file:
    #     file.write(soup.prettify())

    markets = list(map(Market, (
        item.text.strip() for item in soup.select('div.content table tbody tr td:nth-child(3)')
    )))

    result = [Market('ROW')]
    for market in markets:

        common_params = {'mkt': str(market), 'setlang': market.lang, 'cc': market.country}
        data = requests.get(
            'https://www.bing.com/HPImageArchive.aspx',
            params={'format': 'js', 'idx': 0, 'n': 10} | common_params
        ).json()['images']

        url = 'https://bing.com' + data[0]['urlbase']

        if extract_market_from_url(url) == market:
            result.append(market)

    return result


if __name__ == '__main__':
    regions = get_regions()
    print(list(map(str, regions)))  # Can be copied to src/Region.py and website's HTML/JS
    print()

    if regions == REGIONS:
        print('✅ Regions are up-to-date')
    else:
        warn('Regions are outdated. Please update src/Region.py')
        print('Old regions:', REGIONS)
        print('New regions:', regions)
