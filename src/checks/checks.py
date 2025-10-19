from collections import Counter
from datetime import timedelta
import sys

sys.path.append('../')
from Region import REGIONS


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def print_percentage(a, b):
    return f'{a / b * 100:.2f}% ({a}/{b})'


def run_checks():
    for region in REGIONS:
        api = region.read_api()

        # Report missing dates
        existing_dates = [item.date for item in api]
        for date in daterange(api[0].date, api[-1].date):
            if date not in existing_dates:
                print(f'{repr(region)} is missing {date}')

        # Report missing Bing URLs (statistics)
        without_url = [item for item in api if not item.bing_url]
        if without_url:
            print(f'\n{repr(region)} has {print_percentage(len(without_url), len(api))} images without Bing URL')

        # Report missing URLs (statistics)
        without_url = [item for item in api if not item.url]
        if without_url:
            print(f'\n{repr(region)} has {print_percentage(len(without_url), len(api))} images without URL')

        # Check that no urls overlap
        urls_counter = Counter(item.url for item in api)
        if len(urls_counter) != len(api):
            print(f'\n{repr(region)} has duplicate urls:')
            for url, count in urls_counter.items():
                if count > 1:
                    print(url)


if __name__ == '__main__':
    run_checks()
