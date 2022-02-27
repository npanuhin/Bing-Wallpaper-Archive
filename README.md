<h1 align="center">Bing Wallpaper Archive</h1>

<div align="center">
    <a href="https://github.com/npanuhin/bing-wallpaper-archive/actions/workflows/check_images.yml">
        <img alt="" src="https://github.com/npanuhin/bing-wallpaper-archive/actions/workflows/check_images.yml/badge.svg?event=push">
    </a>
    <a href="https://github.com/npanuhin/bing-wallpaper-archive/actions/workflows/daily_update.yml">
        <img alt="Last image: 2022-02-27" src="https://img.shields.io/static/v1?label=Last%20image&message=2022-02-27&color=informational&style=flat">
    </a>
<!-- <img alt="Updated on: 2022-01-05" src="https://img.shields.io/static/v1?label=Updated%20on&message=2022-01-05&color=informational&link=https://github.com/npanuhin/bing-wallpaper-archive/actions/workflows/daily_update.yml&link=https://github.com/npanuhin/bing-wallpaper-archive/raw/master/api/US/images/2022-01-05.jpg"> -->
</div>


![](api/US/images/2022-02-27.jpg)


### Development

**[ExifTool](https://exiftool.org)**
-  *Windows*: [Download](https://npanuhin.me/files/exiftool.exe) ([mirror1](https://exiftool.org/exiftool-12.38.zip), [mirror2](https://oliverbetz.de/cms/files/Artikel/ExifTool-for-Windows/ExifTool_install_12.38_64.exe), change filename) to [`/src/exiftool`](src/exiftool).
-  *Linux*: [Download](https://npanuhin.me/files/Image-ExifTool-12.38.tar.gz) ([mirror](https://exiftool.org/Image-ExifTool-12.38.tar.gz)) and unpack to [`/src/exiftool`](src/exiftool):
    ```bash
    wget https://npanuhin.me/files/Image-ExifTool-12.38.tar.gz
    gzip -dc Image-ExifTool-12.38.tar.gz | tar -xf - --strip-components=1
    ```


### TODO

-  **"copyright" field has last character strippped (!)**
-  GitHub api for badges (done?)
-  `caption = subtitle`  -> `subtitle/caption = None`
