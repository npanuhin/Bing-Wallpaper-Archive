from datetime import datetime, timedelta
import sys

sys.path.append('../')
from Region import REGIONS  # noqa: E402


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def print_percentage(a, b):
    return f'{a / b * 100:.2f}% ({a}/{b})'


def check_status():
    for region in REGIONS:
        api = region.read_api()

        # Check that all dates are present
        start_date = datetime.strptime(api[0]['date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(api[-1]['date'], "%Y-%m-%d").date()
        existing_dates = [item['date'] for item in api]
        missing_dates = []
        for date in daterange(start_date, end_date):
            date = date.strftime("%Y-%m-%d")
            if date not in existing_dates:
                missing_dates.append(date)

        if missing_dates:
            for missing_date in missing_dates:
                print(f'{region.mkt} is missing {missing_date}')

        # Check how many images are missing Bing URL
        without_url = [item for item in api if not item['bing_url']]
        if without_url:
            print(f'\n{region.mkt} has {print_percentage(len(without_url), len(api))} images without Bing URL')

        # Check how many images are missing URL
        without_url = [item for item in api if not item['url']]
        if without_url:
            print(f'\n{region.mkt} has {print_percentage(len(without_url), len(api))} images without URL')

        # Check that no urls overlap
        urls = [item['url'] for item in api]
        if len(urls) != len(set(urls)):
            print(f'\n{region.mkt} has duplicate urls:')
            for url in urls:
                if urls.count(url) > 1:
                    print(url)


if __name__ == '__main__':
    check_status()
