"""Export every BMG in the ROM to translation/<path>.json.

Existing translations ("et") are preserved when re-exporting.
"""
import json
import os
import ndspy.rom

import bmg
import tables

ROM = 'rom/Animal Crossing - Wild World (USA) (Rev 1).nds'
OUT = 'translation'
SKIP = {'script/ENG/message/sp/npc/test_.bmg'}  # Japanese debug text


def main():
    rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
    files = msgs = 0
    for fid, data in enumerate(rom.files):
        path = rom.filenames.filenameOf(fid)
        if not path or not path.endswith('.bmg') or path in SKIP:
            continue
        b = bmg.Bmg(bmg.unwrap(data))
        dst = os.path.join(OUT, path[len('script/ENG/'):-4] + '.json')
        old = {}
        if os.path.exists(dst):
            old = {e['id']: e for e in json.load(open(dst, encoding='utf-8'))['messages']}
        entries = []
        for i, m in enumerate(b.messages):
            if not m:
                continue
            en = bmg.decode(m)
            prev = old.get(i, {})
            entries.append({'id': i, 'en': en, 'et': prev.get('et', '')})
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w', encoding='utf-8') as f:
            json.dump({'file': path, 'messages': entries}, f, ensure_ascii=False, indent=1)
            f.write('\n')
        files += 1
        msgs += len(entries)
    print(f'exported {msgs} messages from {files} files')
    print(f'exported {tables.export(rom)} names from {len(tables.TABLES)} tables')


if __name__ == '__main__':
    main()
