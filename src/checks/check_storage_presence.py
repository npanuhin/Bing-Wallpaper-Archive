from threading import Thread
import sys

import requests

sys.path.append('../')
from Region import REGIONS


def check_url(url):
    response = requests.head(url)
    if response.status_code != 200:
        print(f'\n{url} has status code {response.status_code}')
    else:
        print('✓', end='')


def check_storage_presence():
    threads = []

    for region in REGIONS:
        api = region.read_api()

        for item in api:
            url = item.url

            thread = Thread(target=check_url, args=(url,))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    check_storage_presence()
