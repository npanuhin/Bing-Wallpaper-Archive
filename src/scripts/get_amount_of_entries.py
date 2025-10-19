import sys

sys.path.append('../')
from Region import REGIONS


def get_amount_of_entries():
    amount = 0

    for region in REGIONS:
        api = region.read_api()
        amount += len(api)

    print(amount)


if __name__ == '__main__':
    get_amount_of_entries()
