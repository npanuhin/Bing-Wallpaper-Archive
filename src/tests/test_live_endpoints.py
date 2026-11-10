import urllib.request
import pytest

BASE_URL = 'https://bing.npanuhin.me'

LIVE_ENDPOINTS = [
    # All endpoints
    '/all.json',
    '/all.min.json',

    # Entire region - canonical and rewritten (dashed)
    '/US/en.json',
    '/US/en.min.json',
    '/US-en.json',
    '/US-en.min.json',
    '/ROW/en.json',
    '/ROW-en.json',

    # Region by year - dotted and nested and rewritten
    '/US/en.2024.json',
    '/US/en.2024.min.json',
    '/US/en/2024.json',
    '/US/en/2024.min.json',
    '/US-en.2024.json',
    '/US-en.2024.min.json',

    # Region by month - dotted and nested and rewritten
    '/US/en.2024.01.json',
    '/US/en.2024.01.min.json',
    '/US/en/2024.01.json',
    '/US/en/2024.01.min.json',
    '/US-en.2024.01.json',
    '/US-en.2024.01.min.json',

    # Images / Media rewrites
    '/US/en/2024-01-01.jpg',
    '/US-en/2024-01-01.jpg',
    '/US-en-2024-01-01.jpg',

    # Website static pages
    '/',
    '/status',
]


@pytest.mark.live
@pytest.mark.parametrize('path', LIVE_ENDPOINTS)
def test_live_endpoint(path: str):
    url = f'{BASE_URL}{path}'
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Bing-Wallpaper-Archive Live Test)'}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        assert res.status == 200, f'Expected 200 for {url}, got {res.status}'
        content_type = res.headers.get('Content-Type', '')
        if path.endswith('.json'):
            assert 'application/json' in content_type or 'text/json' in content_type
        elif path.endswith('.jpg'):
            assert 'image/jpeg' in content_type
