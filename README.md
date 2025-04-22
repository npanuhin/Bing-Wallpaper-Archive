<h1 align="center">Bing Wallpaper Archive</h1>

<div align="center">
    <a id="last_image_link" href="https://bing.npanuhin.me/US/en/2025-04-22.jpg">
        <img id="last_image" title="Grand Prismatic Spring, Yellowstone National Park, Wyoming" alt="Grand Prismatic Spring, Yellowstone National Park, Wyoming" src="https://bing.npanuhin.me/US/en/2025-04-22.jpg">
        <img id="last_image_badge" alt="Last image: 2025-04-22" src="https://img.shields.io/badge/Last_image-2025--04--22-informational?style=flat">
    </a>
</div>

### Usage

All information is stored in "API files"[^1]. They can be obtained by sending a GET request to the following URL:

```haskell
https://bing.npanuhin.me/{country}/{language}.json
```
<!-- https://bing.npanuhin.me/{country}/{language}.url.json  # Only dates and urls (format description below) -->

The following countries and languages are currently available:
<table>
    <thead>
        <tr>
            <th width="500px">United States</th>
            <th width="500px">Canada (English)</th>
            <th width="500px">Italy</th>
            <th width="500px">Spain</th>
            <th width="500px">France</th>
            <th width="500px">Germany</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center" title="United States: in English">
                <a href="https://bing.npanuhin.me/US/en.json"><code>US/en</code></a>
            </td>
            <td align="center" title="Canada: in English">
                <a href="https://bing.npanuhin.me/CA/en.json"><code>CA/en</code></a>
            </td>
            <td align="center" title="Italy: in Italian">
                <a href="https://bing.npanuhin.me/IT/it.json"><code>IT/it</code></a>
            </td>
            <td align="center" title="Spain: in Spanish">
                <a href="https://bing.npanuhin.me/ES/es.json"><code>ES/es</code></a>
            </td>
            <td align="center" title="France: in French">
                <a href="https://bing.npanuhin.me/FR/fr.json"><code>FR/fr</code></a>
            </td>
            <td align="center" title="Germany: in German">
                <a href="https://bing.npanuhin.me/DE/de.json"><code>DE/de</code></a>
            </td>
        </tr>
        <tr>
            <th>United Kingdom</th>
            <th>Canada (French)</th>
            <th>India</th>
            <th>China</th>
            <th>Japan</th>
            <th>Brazil</th>
        </tr>
        <tr>
            <td align="center" title="United Kingdom: in English">
                <a href="https://bing.npanuhin.me/GB/en.json"><code>GB/en</code></a>
            </td>
            <td align="center" title="Canada: in French">
                <a href="https://bing.npanuhin.me/CA/fr.json"><code>CA/fr</code></a>
            </td>
            <td align="center" title="India: in English">
                <a href="https://bing.npanuhin.me/IN/en.json"><code>IN/en</code></a>
            </td>
            <td align="center" title="China: in Chinese">
                <a href="https://bing.npanuhin.me/CN/zh.json"><code>CN/zh</code></a>
            </td>
            <td align="center" title="Japan: in Japanese">
                <a href="https://bing.npanuhin.me/JP/ja.json"><code>JP/ja</code></a>
            </td>
            <td align="center" title="Brazil: in Portuguese">
                <a href="https://bing.npanuhin.me/BR/pt.json"><code>BR/pt</code></a>
            </td>
        </tr>
        <tr>
            <td colspan="6" align="center" title="Rest of The World: in English">
                <b>Rest of The World:</b>   <a href="https://bing.npanuhin.me/ROW/en.json"><code>ROW/en</code></a> 
            </td>
        </tr>
    </tbody>
</table>


One API file consists of an array of image data[^2]:
```jsonc
[
    // Types and descriptions:
    {
        "title": "Title" | null,
        "caption": "Caption" | null,
        "subtitle": "Subtitle" | null,
        "copyright": "Copyright" | null,
        "description": "Description" | null,
        "date": "Date in %Y-%m-%d format with leading zeros",
        "bing_url": "Bing URL" | null,
        "url": "Storage URL: https://bing.npanuhin.me/{country}/{language}/{date}.jpg"
    },
    // Example:
    {
        "title": "Example title",
        "caption": "Example caption",
        "subtitle": "Example subtitle",
        "copyright": "npanuhin/Bing Wallpaper Archive ©",
        "description": "Example description\nThat can span multiple lines",
        "date": "2009-06-03",
        "bing_url": null,
        "url": "https://bing.npanuhin.me/US/en/2024-01-16.jpg"
    }
]
```

- Images are sorted by `date` in ascending order (oldest first, newest last)

- The `bing_url` field contains the original image URL from Bing (Microsoft) servers. Unfortunately, it is not possible to retrieve images from more than a couple of years ago from these URLs (they all point to the same dummy image)

<!-- URL API files are minified and contain only `date` field as key and `url` field as value (to save space as much as possible):
```jsonc
{"2009-06-03":"https://bing.npanuhin.me/US/en/2009-06-03.jpg","...":"...",}
``` -->

> [!NOTE]
> API files tend to be quite large (a couple of MB)

> [!TIP]
> If you only need images, **you can skip loading the API files altogether**! Simply make a request to the storage URL using the format specified above (if 404 is returned, then sadly we don't have this image).
>
> If you still need image titles, descriptions, etc., but want to save bandwidth, you can get API files for specific years:
> ```haskell
> https://bing.npanuhin.me/{country}/{language}.{year}.json
> ```
> For example: <a href="https://bing.npanuhin.me/US/en.2021.json"><code>US/en.2021</code></a> or <a href="https://bing.npanuhin.me/ROW/en.2024.json"><code>ROW/en.2024</code></a><br>
> These files are minified and typically have a size of 100-500 KB. If 404 is returned, then we don't have any images for that year


<!-- >
> **Pro tip**:  
> If you only need images, **you can skip loading the API files altogether**! Simply make a request to the storage URL using the format specified above (if 404 is returned, then sadly we don't have this image) -->


<!-- If you don't need image titles, descriptions, etc., you can use the URL API file, which is *only about 13% the size* of the full API file: -->
<!-- > [!TIP]
> If you only need images, **you can skip loading the API files altogether**! Simply make a request to the storage URL using the format specified above (if 404 is returned, then sadly we don't have this image) -->

> [!IMPORTANT]
> Feel free to use the API files and images, but please **avoid sending frequent requests** (for images this would incur additional costs for me).
>
> If you need to make frequent requests to the API files, I recommend downloading and caching them locally (they are updated only once a day). The same applies to the images (although this will be quite difficult to implement).
>
> Your understanding and cooperation are greatly appreciated 🙂


### Version 2 roadmap

After two years, I decided to rewrite the entire project and to fix numerous issues, including storage capacity and metadata.

Stages (roughly in order of importance):

- [ ] ! Fix `en` not working for Canada (urgent)
- [x] Proper everyday image retrieval from three sources
- [x] Uploading images to external storage (chose ~~Google Cloud Storage~~ Cloudflare R2 for now)
- [x] Removing metadata nonsense — images should be preserved in their original form
- [x] Upload all images to storage
- [x] Replace spaces by `\t` in API to reduce space
- [ ] Fix metadata for all images (currently done: ?/?)
- [x] Finally remove all images from this repo and reduce the size of repo (+ number of commits in repo)
- [x] Remove the `path` key
- [x] Generate API only for website and not store it in Git repo (+ minified)
- [ ] Write a comprehensive README
- [x] Enable other countries
- [x] Rewrite website
- [x] Website: hold current image when hovering over title
- [ ] Website: Maybe show the latest image as the first one + preload it sooner than JS script would do it
- [ ] Website: fade-in not just body but all elements
- [ ] ~~Add protection for GCloud (because 5s per image \~= 500'000 images per month if somebody decides to leave the page open for so long xd)~~ Switched to Cloudflare R2
- [ ] Deal with integrity errors (see [TODO](#todo) below)
- [ ] Update (and upload to storage) videos, if needed
- [ ] Find a way to retrieve videos from Bing (identify that today's image is a video, etc.)


### TODO

- Ability to download full acrhive from Cloudflare R2 as `.zip`
- **Missing images (!)** (`src/check_status.py` shows 4 images)
    UPD: probably those are videos, need to check
- Add more images from 2009
- Videos update

<!-- -  `2016-06-05` copyright: `© Heinz Wohner/Getty Images` vs `© Richard Du Toit/Minden Pictures` -->

- Multiple months are missing one image on the last day
- Month `2016-02` has two duplicate images and is missing one image


### Copyright

All images are property of their respective owners (Microsoft, Getty Images, etc.), see the `copyright` field for more details.

Microsoft's official statement regarding wallpaper downloads is: "**Use of this image is restricted to wallpaper only.**"


[^1]: These files are not a typical [API](https://en.wikipedia.org/wiki/API), but they are used to retrieve all valuable information. In some sense they are the Interface of my Application (though not really a Programming Interface)

[^2]: Although the `title` field is optional, de facto every image has a proper title, and this also applies to new images
