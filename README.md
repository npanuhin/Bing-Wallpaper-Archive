<h1 align="center">Bing Wallpaper Archive</h1>

<div align="center">
    <a id="last_image_link" href="https://storage.googleapis.com/npanuhin-bing-wallpaper-archive/US/en/2023-12-17.jpg">
        <img id="last_image" title="Bohemian waxwings perched on a branch, Canada" alt="Bohemian waxwings perched on a branch, Canada" src="https://storage.googleapis.com/npanuhin-bing-wallpaper-archive/US/en/2023-12-17.jpg">
        <img id="last_image_badge" alt="Last image: 2023-12-17" src="https://img.shields.io/badge/Last_image-2023--12--17-informational?style=flat">
    </a>
</div>


### Version 2 roadmap

After two years, I decided to rewrite the entire project and fix numerous issues including storage capacity and metadata.

Stages (roughly in order of importance):

- [x] Proper everyday image retrieval from three sources
- [x] Uploading images to external storage (chose Google Cloud for now)
- [x] Removing metadata nonsense — images should be preserved in their original form
- [x] Upload alll images to storage
- [x] Replace spaces by `\t` in api to reduce space
- [ ] Fix metadata for all images (currently done: ?/?)
- [x] Finally remove all images from this repo and reduce the size of repo (+ number of commits in repo)
- [x] Remove `path` key
- [ ] Write a comprehensive README
- [ ] Enable other countries
- [ ] Improve website + add protection for GCloud (because 5s per image ~= 500'000 images per month if sombody decides to leave the page open for so long xd)
- [ ] Deal with integrity errors (see [TODO](#todo) below)
- [ ] Update (and upload to storage) videos, if needed
- [ ] Find a way to retrieve videos from Bing (identify that today's image is a video, etc.)


### Usage

All information is stored in "API files"[^1]. They can be obtained by sending a GET request to the following URL:

```ruby
https://bing.npanuhin.me/{country}/{language}.json
https://bing.npanuhin.me/{country}/{language}.min.json  # For minified version
```

The following countries and languages are currently available: <a href="https://bing.npanuhin.me/US/en.json"><code>US/en</code></a>

One API file consists of an array of image data:
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
        "path": "Path to image in this repo: {country}/{language}/{date}.jpg",  // To be removed in v2
        "bing_url": "Bing URL" | null,
        "url": "Storage URL: https:/{storage_url}/{country}/{language}/{date}.jpg" | null  // After v2 this field will be required (no null)
    },
    // Example:
    {
        "title": "Example title",
        "caption": "Example caption",
        "subtitle": "Example subtitle",
        "copyright": "npanuhin/Bing Wallpaper Archive ©",
        "description": "Example description\nThat can span multiple lines",
        "date": "2009-06-03",
        "path": "US/en/2009-06-03.jpg",
        "bing_url": null,
        "url": "https://{storage_url}/US/en/2009-06-03.jpg"
    },
]
```

- Images are sorted by `date` in ascending order (oldest first, newest last)

- The `bing_url` field contains the original image URL from Bing (Microsoft) servers. Unfortunately, it is not possible to retrieve images from more than a couple of years ago from these URLs (they all point to the same dummy image)

> [!NOTE]
> API files tend to be quite large (a couple of MB). Use a minimified version in production environments

> [!TIP]
> Feel free to use the API files and images, but please **avoid sending frequent requests** (for images this would incur additional costs for me on Google Cloud Storage).
>
> <a name="sometext"></a>If you need to make frequent requests to the API files, I recommend downloading and caching them locally (they are updated only once a day). The same applies to the images (although this will be quite difficult to implement)
>
> Your understanding and cooperation are greatly appreciated 🙂


### TODO

- **Missing images (!)** (`src/check_status.py` shows 4 images)
    UPD: probably those are videos, need to check
- Add more images from 2009
- Videos update

<!-- -  `2016-06-05` copyright: `© Heinz Wohner/Getty Images` vs `© Richard Du Toit/Minden Pictures` -->

- Multiple months are missing one image on the last day
- Month `2016-02` has two duplicate images and is missing one image


[^1]: These files are not a typical [API](https://en.wikipedia.org/wiki/API), but they are used to retrieve all valuable information. In some sence they are the Interface of my Application (though not really a Programming Interface)

### Copyright

All images are property of their respective owners (Microsoft, Getty Images, etc.), see the `copyright` field for more details.

Microsoft's official statement regarding wallpaper downloads is: "**Use of this image is restricted to wallpaper only.**"
