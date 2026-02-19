import re
import sys

sys.path.append('../')

from ApiChecker import checker  # type: ignore
from Region import Region  # type: ignore

TEXT_FIELDS = ['title', 'caption', 'subtitle', 'copyright', 'description']
NBSP = '\u00a0'
NNBSP = '\u202f'


@checker.check_field(*TEXT_FIELDS)
def check_dashes(value: str, region: Region):
    other_dashes = '‐‑‒–—―⁓⁃−'
    for m in re.finditer(r'\S*\s+-\s*\S*|\S*-\s+\S*', value):
        yield f'Dash with spaces: {m.group(0)}'
    for m in re.finditer(rf'\S*(\S[{other_dashes}]|[{other_dashes}]\S)\S*', value):
        yield f'Dash without spaces: {m.group(0)}'


@checker.check_field(*TEXT_FIELDS)
def check_number_near_letter(value: str, region: Region):
    for m in re.finditer(r'\d[^\W\d_ºª]|[^\W\d_ºª]\d', value):
        if not re.search(r'\b\d+(st|nd|rd|th|s)\b', value, re.IGNORECASE):
            yield f'Number near letter: {m.group(0)}'


@checker.check_field(*TEXT_FIELDS)
def check_strange_characters(value: str, region: Region):
    for char in value:
        cp = ord(char)
        if cp < 32 and char not in '\n\r':
            yield f'Control character ({cp}): {char}'
        elif cp == 0x0009:
            yield f'Tab character: {char}'
        elif cp == 0xFFFD:
            yield f'Replacement character: {char}'
        elif 0x200B <= cp <= 0x200F or 0x202A <= cp <= 0x202E:
            yield f'Invisible formatting character ({hex(cp)}): {char}'
        elif cp > 0xFFFF:
            if not (0x1F300 <= cp <= 0x1F9FF):
                yield f'High Unicode character ({hex(cp)}): {char}'


@checker.check_field(*TEXT_FIELDS)
def check_non_standard_whitespace(value: str, region: Region):
    is_french = region.lang == 'fr'
    for m in re.finditer(r'[^\S\r\n ]', value):
        char = m.group(0)
        if is_french and char == NNBSP:
            continue
        yield f'Non-standard whitespace: {char}'


@checker.check_field(*TEXT_FIELDS)
def check_repeating_characters(value: str, region: Region):
    for m in re.finditer(r'[!?]{2,}', value):
        if not re.fullmatch(r'\?!+', m.group(0)):
            yield f'Multiple punctuation marks: {m.group(0)}'
    for m in re.finditer(r'[^\s.]*(\.{2,})[^\s.]*', value):
        dots = m.group(1)
        if len(dots) == 2:
            yield f'Double dot: {m.group(0)}'
        elif len(dots) >= 4:
            yield f'Too many repeating characters: {m.group(0)}'
    for m in re.finditer(r'([^.])\1\1\1+', value):
        yield f'Too many repeating characters: {m.group(0)}'


@checker.check_field(*TEXT_FIELDS)
def check_punctuation_spacing(value: str, region: Region):
    is_french = region.lang == 'fr'
    french_punc = ':;?!'

    # Space before punctuation
    for m in re.finditer(r'(?P<before>\S*)(?P<spaces>\s+)(?P<char>[.,!?;:])(?P<after>\S*)', value):
        match_str, spaces, char = m.group(0), m.group('spaces'), m.group('char')
        if is_french and char in french_punc:
            if spaces != NNBSP:
                yield f'Wrong space before punctuation: {match_str}'
        else:
            yield f'Space before punctuation: {match_str}'

    if is_french:
        for m in re.finditer(rf'\S*(\S([{french_punc}]))\S*', value):
            match_str, char = m.group(0), m.group(2)
            yield f"No space before punctuation': {match_str}"

    # Missing space after punctuation
    quotes = '\'""“”‘’«»'
    for m in re.finditer(rf'\S*[!?][^\s\d{quotes}!?.,)]\S*', value):
        yield f'No space after punctuation: {m.group(0)}'
    for m in re.finditer(rf'\S*[,;:][^\s\d{quotes},;:]\S*', value):
        yield f'No space after punctuation: {m.group(0)}'
    for m in re.finditer(rf'\S*\.[^\s\d{quotes}.A-Z)ºª]\S*', value):
        if not (m.group(0).endswith(('.?', '.!')) and m.group(0).count('.') >= 3):
            match_str = m.group(0)
            if not (match_str.endswith(('.?', '.!')) and '..' in match_str):
                yield f'No space after dot: {match_str}'


if __name__ == '__main__':
    checker.run()
