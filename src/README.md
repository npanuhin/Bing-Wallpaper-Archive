## Cloudflare tokens

Tokens and IDs should be placed into the <code><a href="configs">configs</a>/cloudflare_token.json</code> file:

```json
{
  "CLOUDFLARE_ACCOUNT_ID": "<----->",
  "CLOUDFLARE_R2_ACCESS_KEY_ID": "<----->",
  "CLOUDFLARE_R2_API_TOKEN": "<----->"
}
```

Alternatively, you can set environment variables `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_R2_ACCESS_KEY_ID` and
`CLOUDFLARE_R2_API_TOKEN`.

## Development information

(in no particular order)

> Microsoft does not embed any watermarks in Bing pictures except for the 1920x1200 format when it is available (not
> systematic)

### TODO

Roughly in order of ~~ease of implementation~~ importance:

- Ability to download full acrhive from Cloudflare R2 as `.zip` (e.g. for backup)

- [ ] !!! Setup up alerts (e.g. failed workflow) for integrity errors (super urgent)
- [ ] ~~!! Fix `en` not working for Canada (urgent)~~ ???
- [ ] Fix `CA/en` second day not having `title`
- [x] Proper everyday image retrieval from three sources
- [x] Uploading images to external storage (chose ~~Google Cloud Storage~~ Cloudflare R2 for now)
- [x] Removing metadata nonsense — images should be preserved in their original form
- [x] Upload all images to storage
- [x] Replace spaces by `\t` in API to reduce space
- [ ] Fix metadata for all images (currently done: ?/?)
- [x] Finally remove all images from this repo and reduce the size of repo (+ number of commits in repo)
- [x] Remove the `path` key
- [x] Generate API only for website and not store it in Git repo (+ minified)
- [x] Write a comprehensive README
- [x] Enable other countries
- [x] Rewrite website
- [ ] Website: hold current image when hovering over title
- [x] Website: Maybe show the latest image as the first one + preload it sooner than JS script would do it
- [ ] Website: fade-in not just body but all elements  (??? body is better?)
- [x] ~~Add protection for GCloud (because 5s per image \~= 500'000 images per month if somebody decides to leave the
  page open for so long xd)~~ Switched to Cloudflare R2
- [ ] On the previous note: still add a fail-safe functionality to disable the slideshow after N hours (24?)
- [ ] Deal with integrity errors (see [TODO](#todo) below)
- [ ] Update (and upload to storage) videos, if needed
- [ ] Find a way to retrieve videos from Bing (identify that today's image is a video, etc.)
- [ ] Cache `wrangler` (website deployment)


- **Missing images (!)** (`src/check_status.py` shows 4 images)
  UPD: probably those are videos, need to check
- Add more images from 2009
- Videos update

<!-- -  `2016-06-05` copyright: `© Heinz Wohner/Getty Images` vs `© Richard Du Toit/Minden Pictures` -->

- Multiple months are missing one image on the last day
- Month `2016-02` has two duplicate images and is missing one image
