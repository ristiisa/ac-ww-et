"""Render NSBTX textures (grayscale, palette index) to contact sheets in
extracted/tex/ so text on 3D textures (signs etc.) can be spotted.
Usage: texsheet.py <rom dir prefix>...   e.g. texsheet.py str/ bg/"""
import os
import struct
import sys

import ndspy.lz10
import ndspy.rom
from PIL import Image, ImageDraw

ROM = 'rom/Animal Crossing - Wild World (USA) (Rev 1).nds'
OUT = 'extracted/tex'
BPP = {1: 8, 2: 2, 3: 4, 4: 8, 5: 2, 6: 8, 7: 16}


def textures(data):
    if data[:4] == b'LZ77':
        data = ndspy.lz10.decompress(data[4:])
    if data[:4] != b'BTX0':
        return
    tex0 = struct.unpack_from('<I', data, 0x10)[0]
    t = data[tex0:]
    info_off = struct.unpack_from('<H', t, 0x0E)[0]
    data_off = struct.unpack_from('<I', t, 0x14)[0]
    comp_off = struct.unpack_from('<I', t, 0x24)[0]
    count = t[info_off + 1]
    p = info_off + 4
    p += struct.unpack_from('<H', t, p)[0] + 4 * count  # skip unknown block
    p += 4
    params = [struct.unpack_from('<I', t, p + 8 * i)[0] for i in range(count)]
    names = [t[p + 8 * count + 16 * i:p + 8 * count + 16 * (i + 1)].split(b'\0')[0].decode('latin1')
             for i in range(count)]
    for name, prm in zip(names, params):
        fmt = (prm >> 26) & 7
        if not fmt:
            continue
        w, h = 8 << ((prm >> 20) & 7), 8 << ((prm >> 23) & 7)
        off = ((prm & 0xFFFF) << 3) + (comp_off if fmt == 5 else data_off)
        raw = t[off:off + w * h * BPP[fmt] // 8]
        yield name, _gray(fmt, w, h, raw)


def _gray(fmt, w, h, raw):
    img = Image.new('L', (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if fmt == 5:  # 4x4 blocks, 2bpp per texel
                bi = (y // 4) * (w // 4) + x // 4
                if bi * 4 + 4 > len(raw):
                    continue
                v = (raw[bi * 4 + y % 4] >> (2 * (x % 4))) & 3
                px[x, y] = v * 85
                continue
            i = y * w + x
            bpp = BPP[fmt]
            if (i * bpp) // 8 >= len(raw):
                continue
            if bpp == 16:
                c = struct.unpack_from('<H', raw, i * 2)[0]
                px[x, y] = ((c & 31) + ((c >> 5) & 31) + ((c >> 10) & 31)) * 255 // 93
            else:
                b = raw[(i * bpp) // 8]
                v = (b >> ((i * bpp) % 8)) & ((1 << bpp) - 1)
                if fmt == 1:
                    v &= 31; bpp = 5
                elif fmt == 6:
                    v &= 7; bpp = 3
                px[x, y] = v * 255 // ((1 << bpp) - 1)
    return img


def main(prefixes):
    rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
    items = []
    for fid in range(len(rom.files)):
        p = rom.filenames.filenameOf(fid)
        if p and p.endswith('.nsbtx') and p.startswith(tuple(prefixes)):
            try:
                for name, img in textures(bytes(rom.files[fid])):
                    items.append((f'{p}:{name}', img))
            except Exception as e:
                print('skip', p, e)
    os.makedirs(OUT, exist_ok=True)
    tag = '_'.join(x.strip('/').replace('/', '-') for x in prefixes)
    W, H = 1100, 1600
    page, x, y, rowh, n = Image.new('L', (W, H), 40), 0, 0, 0, 0
    for label, img in items:
        s = 2 if max(img.size) <= 128 else 1
        im = img.resize((img.width * s, img.height * s), Image.NEAREST)
        if x + max(im.width, 130) > W:
            x, y, rowh = 0, y + rowh, 0
        if y + im.height + 12 > H:
            page.save(f'{OUT}/{tag}_{n:02d}.png'); n += 1
            page, x, y, rowh = Image.new('L', (W, H), 40), 0, 0, 0
        ImageDraw.Draw(page).text((x, y), label.split('/')[-1][:24], fill=255)
        page.paste(im, (x, y + 11))
        x += max(im.width, 130) + 4
        rowh = max(rowh, im.height + 13)
    page.save(f'{OUT}/{tag}_{n:02d}.png')
    print(len(items), 'textures,', n + 1, 'sheets')


if __name__ == '__main__':
    main(sys.argv[1:])
