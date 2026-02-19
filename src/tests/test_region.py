from Region import extract_market_from_url, Market, Region


def test_extract_market_from_url():
    assert extract_market_from_url(
        'https://bing.com/th?id=OHR.WhiteEyes_EN-US2249866810_1920x1080.jpg'
    ) == Market('en-US')

    assert extract_market_from_url(
        'https://bing.com/th?id=OHR.WhiteEyes_ROW2172958331_1920x1200.jpg&rf=LaDigue_1920x1200.jpg'
    ) == Market('ROW')


def test_region_str():
    assert str(Region('ROW')) == 'en-ROW'
    assert str(Region('en-US')) == 'en-US'


def test_region_repr():
    assert repr(Region('ROW')) == 'ROW [en-RU]'
    assert repr(Region('en-US')) == 'en-US'
