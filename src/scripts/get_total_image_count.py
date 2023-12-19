import sys

sys.path.append('../')
from Region import REGIONS  # noqa: E402


def main():
    total_image_count = 0

    for region in REGIONS:
        api = region.read_api()

        total_image_count += len(api)

    print(total_image_count)


if __name__ == '__main__':
    main()
