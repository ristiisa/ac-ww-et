"""Check translated lines against the dialogue box limits.

Usage: check.py [translation/*.json ...]   (default: all files)

Line width is measured in pixels with fontA's glyph widths (+1px spacing).
Variables ({04 ..}) are counted as VAR_WIDTH pixels. A page is 3 lines;
choice lines after a {02 ..} code are not part of a page.
"""
import glob
import json
import re
import struct
import sys

import ndspy.lz10

FONT = 'extracted/font/fontA_attr.bin'
MAX_WIDTH = 160  # English dialogue: max 164, 99th percentile 160 (see --calibrate)
VAR_WIDTH = 48   # e.g. an 8-letter player or town name
PAGE_LINES = 3

_attr = open(FONT, 'rb').read()
_attr = ndspy.lz10.decompress(_attr[4:])
WIDTHS = {struct.unpack_from('<H', _attr, i)[0]: struct.unpack_from('<H', _attr, i + 2)[0]
          for i in range(0, len(_attr), 4)}

_CODE = re.compile(r'\{\{|\}\}|\{([0-9a-fA-F ]*)\}')


def width(line):
    w = 0
    pos = 0
    for m in _CODE.finditer(line):
        w += _text_width(line[pos:m.start()])
        if m.group(0) in ('{{', '}}'):
            w += _text_width(m.group(0)[0])
        elif m.group(1).startswith('04'):
            w += VAR_WIDTH
        pos = m.end()
    return w + _text_width(line[pos:])


def _text_width(s):
    return sum(WIDTHS.get(c.encode('cp1252', errors='replace')[0], 5) + 1 for c in s)


def body_lines(text):
    """Lines that are shown in the dialogue box (choice lines stripped)."""
    m = re.search(r'\{02[0-9a-f ]*\}', text)
    return (text[:m.start()] if m else text).split('\n')


# Info boxes (encyclopedia, name lists) are narrower than the dialogue box and
# are not laid out in 3-line pages.
BOX_WIDTH = 100


def profile(path):
    """(max line width, enforce 3-line pages)

    Encyclopedia entries sit in their own narrow box; the other string tables
    are single words pasted into sentences, so only their length matters.
    """
    if '/string/obj_etc_' in path:
        return BOX_WIDTH, False
    if '/string/' in path:
        return None, False
    if '/bbs/' in path:  # a fixed-size board, not a paged dialogue box
        return MAX_WIDTH, False
    return MAX_WIDTH, True


def main(paths):
    problems = 0
    for p in paths:
        maxw, pages = profile(p)
        messages = json.load(open(p, encoding='utf-8'))['messages']
        # The tallest English entry proves how many lines the box can show.
        max_lines = max((len(body_lines(e['en'])) for e in messages), default=0)
        for e in messages:
            if not e['et'] or e['et'] == '{-}':
                continue
            en, et = body_lines(e['en']), body_lines(e['et'])
            if pages and len(et) % PAGE_LINES != len(en) % PAGE_LINES:
                print(f'{p} #{e["id"]}: {len(et)} lines vs English {len(en)}')
                problems += 1
            if not pages and len(et) > max_lines:
                print(f'{p} #{e["id"]}: {len(et)} lines, more than the {max_lines} the box shows')
                problems += 1
            widest_en = max((width(l) for l in en), default=0)
            for n, line in enumerate(et):
                # A line only counts as too wide if it also beats the English
                # line it replaces (variables are only estimated).
                if maxw and (w := width(line)) > maxw and w > widest_en:
                    print(f'{p} #{e["id"]} line {n + 1}: {w}px > {maxw}: {line!r}')
                    problems += 1
            n_en = len(e['en'].split('\n')) - len(en)
            n_et = len(e['et'].split('\n')) - len(et)
            if n_en != n_et:
                print(f'{p} #{e["id"]}: {n_et} choices vs English {n_en}')
                problems += 1
    print(f'{problems} problem(s)')
    return problems


def calibrate():
    ws = []
    for p in glob.glob('translation/message/**/*.json', recursive=True):
        for e in json.load(open(p, encoding='utf-8'))['messages']:
            for line in body_lines(e['en']):
                if '{04' not in line:
                    ws.append(width(line))
    ws.sort()
    print('max', ws[-1], 'p99.9', ws[int(len(ws) * .999)], 'p99', ws[int(len(ws) * .99)])


if __name__ == '__main__':
    if sys.argv[1:] == ['--calibrate']:
        calibrate()
    else:
        sys.exit(1 if main(sys.argv[1:] or [p for p in glob.glob('translation/**/*.json', recursive=True)
                                          if not p.startswith('translation/tables/')]) else 0)
