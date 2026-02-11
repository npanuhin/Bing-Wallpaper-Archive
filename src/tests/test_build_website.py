from unittest.mock import patch
from io import BytesIO
import datetime
import json

from PIL import Image
import pytest

from structures import ApiEntry
from website.build_website import (
    gen_api_endpoints, gen_github_initial_image,
    gen_website_initial_image, update_website_html, add_headers
)


@pytest.fixture
def temp_website_root(tmp_path):
    root = tmp_path / 'root'
    root.mkdir()
    website_root = root / '_website'
    website_root.mkdir()
    return website_root


def test_gen_api_endpoints(temp_website_root):
    # Setup fake data
    api_entry = ApiEntry(
        title='Test Title',
        caption='Test Caption',
        subtitle='Test Subtitle',
        copyright='Test Copyright',
        description='Test Description',
        date=datetime.date(2024, 1, 1),
        bing_url='https://bing.com/image.jpg',
        url='https://example.com/image.jpg'
    )
    region_to_api = {'US-en': [api_entry]}

    with patch('website.build_website.WEBSITE_ROOT', str(temp_website_root)):
        gen_api_endpoints(region_to_api)

    # Verify files existence
    expected_files = [
        'all.json', 'all.min.json',
        'US-en.json', 'US-en.min.json', 'US/en.json',
        'US-en.2024.json', 'US-en.2024.min.json', 'US/en.2024.json',
        'US-en.2024.01.json', 'US-en.2024.01.min.json', 'US/en.2024.01.json'
    ]
    for file in expected_files:
        assert (temp_website_root / file).exists(), f'File {file} does not exist'

    def check_entry(entry):
        assert entry['title'] == 'Test Title'
        assert entry['caption'] == 'Test Caption'
        assert entry['subtitle'] == 'Test Subtitle'
        assert entry['copyright'] == 'Test Copyright'
        assert entry['description'] == 'Test Description'
        assert entry['date'] == '2024-01-01'
        assert entry['bing_url'] == 'https://bing.com/image.jpg'
        assert entry['url'] == 'https://example.com/image.jpg'

    # Verify map files (all.json, all.min.json)
    for filename in ['all.json', 'all.min.json']:
        with open(temp_website_root / filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'US-en' in data
            check_entry(data['US-en'][0])

    # Verify list files
    list_files = [f for f in expected_files if not f.startswith('all.')]
    for filename in list_files:
        with open(temp_website_root / filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 1
            check_entry(data[0])


def test_gen_github_initial_image(temp_website_root, tmp_path):
    # Create a dummy image
    img = Image.new('RGB', (1920, 1080), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_content = img_byte_arr.getvalue()

    # Create dummy template
    template_path = tmp_path / 'latest-template.svg'
    template_path.write_text('<svg>{width}x{height} - {image_url}</svg>')

    webp_path = temp_website_root / 'latest.webp'
    svg_path = temp_website_root / 'latest.svg'

    with patch('website.build_website.README_IMAGE_WEBP_PATH', str(webp_path)), \
        patch('website.build_website.README_IMAGE_SVG_PATH', str(svg_path)), \
        patch('website.build_website.LATEST_IMAGE_SVG_TEMPLATE', str(template_path)):
        gen_github_initial_image(image_content)

    assert webp_path.exists()
    assert svg_path.exists()
    assert svg_path.read_text().startswith('<svg>1920x1080 - data:image/jpeg;base64,')


def test_gen_website_initial_image(temp_website_root):
    img = Image.new('RGB', (160, 90), color='blue')  # 16:9 image
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_content = img_byte_arr.getvalue()

    assets_path = temp_website_root / 'assets'
    image_path = assets_path / 'initial-image.jpg'

    with patch('website.build_website.WEBSITE_ASSETS_PATH', str(assets_path)), \
        patch('website.build_website.WEBSITE_INITIAL_IMAGE_PATH', str(image_path)):
        gen_website_initial_image(image_content)

    assert image_path.exists()
    with Image.open(image_path) as saved_img:
        assert saved_img.size == (1920, 1080)  # Should be resized


def test_update_website_html(temp_website_root):
    index_html = temp_website_root / 'index.html'
    index_html.write_text('Title: {initial_title}, URL: {initial_image_url}, Desc: {initial_description}')

    api_entry = ApiEntry(
        title='New Title',
        url='https://example.com/new.jpg',
        description='New Description',
        date=datetime.date(2024, 1, 1)
    )

    with patch('website.build_website.WEBSITE_ROOT', str(temp_website_root)):
        update_website_html(api_entry)

    content = index_html.read_text()
    assert 'Title: New Title' in content
    assert 'URL: https://example.com/new.jpg' in content
    assert 'Desc: New Description' in content


def test_add_headers(temp_website_root, tmp_path):
    # We need a dummy _headers file in WEBSITE_PATH
    dummy_website_path = tmp_path / 'website'
    dummy_website_path.mkdir()
    headers_src = dummy_website_path / '_headers'
    headers_src.write_text('Header-Content')

    sys_root = tmp_path / 'sys_root'
    sys_root.mkdir()
    headers_dst = sys_root / '_headers'

    with patch('website.build_website.WEBSITE_PATH', str(dummy_website_path)), \
        patch('website.build_website.WEBSITE_SYS_ROOT', str(sys_root)):
        add_headers()

    assert headers_dst.exists()
    assert headers_dst.read_text() == 'Header-Content'
