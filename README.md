<!--suppress HtmlDeprecatedAttribute -->

<h1 align="center">Bing Wallpaper Archive</h1>

<div align="center">
  <a id="last_image_link" href="https://bing.npanuhin.me/ROW/en/2026-02-13.jpg">
    <picture>
      <source srcset="https://bing.npanuhin.me/latest.webp" type="image/webp">
      <img id="last_image" title="Third Thai-Lao Friendship Bridge connecting Laos and Thailand" alt="Third Thai-Lao Friendship Bridge connecting Laos and Thailand" src="https://bing.npanuhin.me/latest.svg">
    </picture>
    <!-- <img id="last_image_badge" alt="Last image: 2025-10-19" src="https://img.shields.io/badge/Last_image-2025--10--19-informational?style=flat"> -->
  </a>
</div>


### Usage

All information is stored in "API files". They can be obtained by sending a GET request to the following URL:

```haskell
https://bing.npanuhin.me/{country}-{language}.json
```

Available countries and languages:
<table>
  <thead>
    <tr>
      <th width="1000px">United States</th>
      <th width="1000px">Canada (English)</th>
      <th width="1000px">Italy</th>
      <th width="1000px">Spain</th>
      <th width="1000px">France</th>
      <th width="1000px">Germany</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center" title="United States: in English">
        <a href="https://bing.npanuhin.me/US-en.json"><code>US-en</code></a>
      </td>
      <td align="center" title="Canada: in English">
        <a href="https://bing.npanuhin.me/CA-en.json"><code>CA-en</code></a>
      </td>
      <td align="center" title="Italy: in Italian">
        <a href="https://bing.npanuhin.me/IT-it.json"><code>IT-it</code></a>
      </td>
      <td align="center" title="Spain: in Spanish">
        <a href="https://bing.npanuhin.me/ES-es.json"><code>ES-es</code></a>
      </td>
      <td align="center" title="France: in French">
        <a href="https://bing.npanuhin.me/FR-fr.json"><code>FR-fr</code></a>
      </td>
      <td align="center" title="Germany: in German">
        <a href="https://bing.npanuhin.me/DE-de.json"><code>DE-de</code></a>
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
        <a href="https://bing.npanuhin.me/GB-en.json"><code>GB-en</code></a>
      </td>
      <td align="center" title="Canada: in French">
        <a href="https://bing.npanuhin.me/CA-fr.json"><code>CA-fr</code></a>
      </td>
      <td align="center" title="India: in English">
        <a href="https://bing.npanuhin.me/IN-en.json"><code>IN-en</code></a>
      </td>
      <td align="center" title="China: in Chinese">
        <a href="https://bing.npanuhin.me/CN-zh.json"><code>CN-zh</code></a>
      </td>
      <td align="center" title="Japan: in Japanese">
        <a href="https://bing.npanuhin.me/JP-ja.json"><code>JP-ja</code></a>
      </td>
      <td align="center" title="Brazil: in Portuguese">
        <a href="https://bing.npanuhin.me/BR-pt.json"><code>BR-pt</code></a>
      </td>
    </tr>
    <tr>
      <td colspan="6" align="center" title="Rest of The World: in English">
        <b>Rest of The World:</b>   <a href="https://bing.npanuhin.me/ROW-en.json"><code>ROW-en</code></a> 
      </td>
    </tr>
  </tbody>
</table>


API files contain image data:
```jsonc
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
    "date": "2024-01-16",
    "bing_url": null,
    "url": "https://bing.npanuhin.me/US/en/2024-01-16.jpg"
}
```


<h3 align="center">Endpoints</h3>

<table>
  <thead>
    <tr>
      <th width="6000px">Scope</th>
      <th width="7000px">Path</th>
      <th width="2000px">Example</th>
      <th width="800px">Size</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Everything</td>
      <td>
        <code>/all.json</code>
      </td>
      <td>
        <a href="https://bing.npanuhin.me/all.json">all.json</a>
      </td>
      <td align="center" id="endpoint_everything_size">
          16 MB ↑
      </td>
    </tr>
    <tr>
      <td>By country</td>
      <td>
        <code>/{country}-{lang}.json</code>
      </td>
      <td>
        <a href="https://bing.npanuhin.me/US-en.json">US-en.json</a>
      </td>
      <td align="center" id="endpoint_country_size">
         1.3 MB ↑
      </td>
    </tr>
    <tr>
      <td>By country and year</td>
      <td>
        <code>/{country}-{lang}.{Y}.json</code>
      </td>
      <td>
        <a href="https://bing.npanuhin.me/US-en.2024.json">US-en.2024.json</a>
      </td>
      <td align="center" id="endpoint_year_size">
         0.3 MB  
      </td>
    </tr>
    <tr>
      <td>By country, year and month</td>
      <td>
        <code>/{country}-{lang}.{Y}.{M}.json</code>
      </td>
      <td>
        <a href="https://bing.npanuhin.me/US-en.2024.01.json">US-en.2024.01.json</a>
      </td>
      <td align="center" id="endpoint_month_size">
        0.04 MB  
      </td>
    </tr>
    <tr>
      <td><b>Image</b></td>
      <td>
        <b><code>/{country}/{lang}/{date}.jpg</code></b>
      </td>
      <td>
        <b><a href="https://bing.npanuhin.me/US/en/2024-01-16.jpg">US/en/2024-01-16.jpg</a></b>
      </td>
      <td align="center" id="endpoint_image_size"><b> 3.4 MB  </b></td>
    </tr>
  </tbody>
</table>


Size column contains an estimated average file size for that type. `↑` means the size will increase with time.

Replace `.json` with `.min.json` to get the files with no indentation.

If 404 error is returned, then sadly, there is no data or image.


> [!TIP]
> If you know the date, you can fetch an image without bothering with API files.

#### Notes on the available data:

Images are sorted by `date` in ascending order (oldest first, newest last).

Although the `title` field is optional, de facto every image has a proper title, and this also applies to new images.

The `bing_url` field contains the original image URL from Bing (Microsoft) servers. Unfortunately, it is not possible to
retrieve images from more than a couple of years ago from these URLs (they all point to the same dummy image).


> [!NOTE]
> You can freely access API files without any frequency or volume limitations.<br>
> As for the images, please download them in reasonable amounts — for example, no more than one full archive per day.


### Copyright

All images are property of their respective owners (Microsoft, Getty Images, etc.),
see the `copyright` field for more details.

Microsoft's statement regarding wallpaper downloads is: "**Use of this image is restricted to wallpaper only.**"
