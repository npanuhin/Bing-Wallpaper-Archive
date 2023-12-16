### Development

**[ExifTool](https://exiftool.org)**
-  *Windows*: [Download](https://npanuhin.me/files/exiftool.exe) ([mirror1](https://exiftool.org/exiftool-12.38.zip), [mirror2](https://oliverbetz.de/cms/files/Artikel/ExifTool-for-Windows/ExifTool_install_12.38_64.exe), change filename) to [`/src/exiftool`](src/exiftool).
-  *Linux*: [Download](https://npanuhin.me/files/Image-ExifTool-12.38.tar.gz) ([mirror](https://exiftool.org/Image-ExifTool-12.38.tar.gz)) and unpack to [`/src/exiftool`](src/exiftool):
    ```bash
    wget https://npanuhin.me/files/Image-ExifTool-12.38.tar.gz
    gzip -dc Image-ExifTool-12.38.tar.gz | tar -xf - --strip-components=1
    ```
