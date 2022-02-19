from collections import defaultdict
from bs4 import BeautifulSoup
import requests
# import datetime
import os

from utils import mkpath, FileDownloader, prettifyDataString, Threads, SafeJson


VIDEOS_API_PATH = mkpath("../", "../", "api", "videos")


# ==========================================================================================================

DOWNLOADER = FileDownloader()
safe_json = SafeJson()


def parseVideoList(video_pages, page_num):
    soup = BeautifulSoup(requests.get("https://peapix.com/videos/p-{}".format(page_num)).text, "lxml")

    for block in soup.findAll("a", class_="video-card__image-container"):
        video_pages.append(block.get("href"))


def main():
    soup = BeautifulSoup(requests.get("https://peapix.com/videos").text, "lxml")

    pages_count = int(soup.find("ul", class_="pagination").find("li", class_="PagedList-skipToLast").find('a').text)

    video_pages = []

    with Threads() as threads:
        for page_num in range(1, pages_count + 1):
            threads.add(parseVideoList, (video_pages, page_num)).start()

    video_pages.sort()

    print("Found {} videos".format(len(video_pages)))

    videos = []

    date_counts = defaultdict(lambda: 0)

    for video_page in video_pages:
        soup = BeautifulSoup(requests.get("https://peapix.com" + video_page).text, "lxml")

        video_link = soup.find("div", class_="modal-dialog--download").find("a").get("href")
        description = prettifyDataString(soup.find("div", class_="gallery-photo-addthis").find_next_sibling("div").find("p").text)
        date = soup.find("time").get("datetime").strip()

        image_path = mkpath(VIDEOS_API_PATH, "source", date + "_" + str(date_counts[date]) + os.path.splitext(video_link)[1])

        if not os.path.isfile(image_path):
            print("Downloading video {} ({})".format(video_page, date))
            DOWNLOADER.download(video_link, image_path)

        videos.append({
            "date": date,
            "description": description if description else None,
            "path": image_path
        })

        date_counts[date] += 1

    videos.sort(key=lambda video: video["date"])

    safe_json.dump(mkpath(VIDEOS_API_PATH, "videos.json"), videos, prettify=True, ensure_ascii=False)


if __name__ == "__main__":
    main()
