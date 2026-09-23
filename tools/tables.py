"""Fixed-size name tables outside the BMG files (item, furniture, series, pattern names).

Each table is an array of equal-sized records with a null-padded cp1252 name
field. Identical English names are grouped into one entry whose "ids" lists
every record using it, so each name is translated once. "max" is the longest
name (in bytes) that fits in the field with its terminator.
"""
import json
import os

import bmg

# ROM path -> (record size, name offset, name field size)
TABLES = {
    'item_info/dma.bin': (20, 2, 18),
    'ftr_info/dma.bin': (28, 11, 17),
    'item_info/series.bin': (20, 1, 19),
    'myOrg/myD.bin': (44, 2, 16),
}
OUT = 'translation/tables'


def json_path(rom_path):
    return os.path.join(OUT, rom_path.replace('/', '_').replace('.bin', '.json'))


def records(rom_path, data):
    size, off, field = TABLES[rom_path]
    for i in range(len(data) // size):
        raw = data[i * size + off:i * size + off + field]
        yield i, bytes(raw.split(b'\0')[0])


def export(rom):
    total = 0
    for rom_path, (size, off, field) in TABLES.items():
        data = rom.getFileByName(rom_path)
        groups = {}
        for i, name in records(rom_path, data):
            if name:
                groups.setdefault(name, []).append(i)
        dst = json_path(rom_path)
        old = {}
        if os.path.exists(dst):
            old = {e['en']: e['et'] for e in json.load(open(dst, encoding='utf-8'))['names']}
        names = []
        for name, ids in groups.items():
            en = bmg.decode(name)
            names.append({'ids': ids, 'en': en, 'et': old.get(en, '')})
        os.makedirs(OUT, exist_ok=True)
        with open(dst, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'file': rom_path, 'max': field - 1, 'names': names},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        total += len(names)
    return total


def apply(rom, errors):
    """Write translated names into the ROM. Returns number of names applied."""
    applied = 0
    for rom_path, (size, off, field) in TABLES.items():
        path = json_path(rom_path)
        if not os.path.exists(path):
            continue
        data = bytearray(rom.getFileByName(rom_path))
        for e in json.load(open(path, encoding='utf-8'))['names']:
            if not e['et']:
                continue
            try:
                name = b'' if e['et'] == '{-}' else bmg.encode(e['et'])
            except (ValueError, UnicodeEncodeError) as ex:
                errors.append(f'{path} {e["en"]!r}: {ex}')
                continue
            if len(name) > field - 1:
                errors.append(f'{path} {e["et"]!r}: {len(name)} bytes > {field - 1}')
                continue
            for i in e['ids']:
                start = i * size + off
                data[start:start + field] = name.ljust(field, b'\0')
            applied += 1
        rom.setFileByName(rom_path, bytes(data))
    return applied
