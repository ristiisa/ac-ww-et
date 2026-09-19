"""Extract script/ and font/ folders from the ROM into extracted/."""
import os, sys, ndspy.rom

ROM = 'rom/Animal Crossing - Wild World (USA) (Rev 1).nds'
OUT = 'extracted'
PREFIXES = ('script/', 'font/')

rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
n = 0
for fid, data in enumerate(rom.files):
    path = rom.filenames.filenameOf(fid)
    if path and path.startswith(PREFIXES):
        dst = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(data)
        n += 1
print(f'extracted {n} files')
