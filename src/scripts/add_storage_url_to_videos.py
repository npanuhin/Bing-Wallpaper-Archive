import sys
import os
import json

sys.path.append('../')
from gcloud import gcloud_url  # noqa: E402
from utils import mkpath  # noqa: E402


def main():
    with open(mkpath('../../api/videos/videos.json'), 'r', encoding='utf-8') as file:
        videos = json.load(file)

    for item in videos:
        item['url'] = gcloud_url(f'videos/source/{os.path.basename(item["path"])}')

    with open(mkpath('../../api/videos/videos.json'), 'w', encoding='utf-8') as file:
        json.dump(videos, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
