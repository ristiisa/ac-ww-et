"""Build out/AC_WW_EST.nds with Estonian text from translation/*.json.

Messages with an empty "et" keep the English text.
"""
import glob
import json
import os
import sys
import ndspy.rom

import bmg

ROM = 'rom/Animal Crossing - Wild World (USA) (Rev 1).nds'
OUT = 'out/AC_WW_EST.nds'


def main():
    rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
    errors = []
    changed = translated = 0
    for jp in sorted(glob.glob('translation/**/*.json', recursive=True)):
        doc = json.load(open(jp, encoding='utf-8'))
        todo = [e for e in doc['messages'] if e['et']]
        if not todo:
            continue
        fid = rom.filenames.idOf(doc['file'])
        b = bmg.Bmg(bmg.unwrap(rom.files[fid]))
        for e in todo:
            try:
                b.messages[e['id']] = bmg.encode(e['et'])
            except (ValueError, UnicodeEncodeError) as ex:
                errors.append(f'{jp} #{e["id"]}: {ex}')
                continue
            if _codes(e['et']) != _codes(e['en']):
                print(f'warning: {jp} #{e["id"]}: control codes differ from English', file=sys.stderr)
            translated += 1
        rom.files[fid] = bmg.wrap(b.build())
        changed += 1
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rom.saveToFile(OUT)
    print(f'{translated} messages in {changed} files -> {OUT}')


def _codes(text):
    return sorted(m.group(0) for m in bmg._TOKEN.finditer(text)
                  if m.group(1) or m.group(2) is not None)


if __name__ == '__main__':
    main()
