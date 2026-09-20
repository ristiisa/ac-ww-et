"""Render 2D tile graphics (menu/*.bch, *_ncg.bin) as grayscale 4bpp tile sheets
into extracted/gfx/, plus labelled contact sheets for quick review."""
import os
import ndspy.lz10
import ndspy.rom
from PIL import Image, ImageDraw

ROM = 'rom/Animal Crossing - Wild World (USA) (Rev 1).nds'
OUT = 'extracted/gfx'


def unlz(d):
    d = bytes(d)
    return ndspy.lz10.decompress(d[4:]) if d[:4] == b'LZ77' else d


def tiles_4bpp(data, cols=16):
    n = len(data) // 32
    rows = (n + cols - 1) // cols
    img = Image.new('L', (cols * 8, max(rows, 1) * 8), 0)
    px = img.load()
    for t in range(n):
        tx, ty = (t % cols) * 8, (t // cols) * 8
        for i in range(32):
            b = data[t * 32 + i]
            y, x = divmod(i * 2, 8)
            px[tx + x, ty + y] = (b & 15) * 17
            px[tx + x + 1, ty + y] = (b >> 4) * 17
    return img


def main():
    rom = ndspy.rom.NintendoDSRom.fromFile(ROM)
    sheets = []
    for fid in range(len(rom.files)):
        p = rom.filenames.filenameOf(fid)
        if not p or not (p.endswith('.bch') or p.endswith('_ncg.bin')):
            continue
        img = tiles_4bpp(unlz(rom.files[fid]))
        dst = os.path.join(OUT, p + '.png')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        img.save(dst)
        sheets.append((p, img))
    # contact sheets: images scaled 2x, stacked with labels, ~1600px tall pages
    page, y, n = Image.new('L', (1100, 1600), 40), 0, 0
    x = 0
    colh = 0
    for p, img in sheets:
        im = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
        h = im.height + 14
        if x + im.width > 1100:
            x, y = 0, y + colh
            colh = 0
        if y + h > 1600:
            page.save(f'{OUT}/sheet_{n:02d}.png'); n += 1
            page, x, y, colh = Image.new('L', (1100, 1600), 40), 0, 0, 0
        ImageDraw.Draw(page).text((x + 2, y), p, fill=255)
        page.paste(im, (x, y + 12))
        x += im.width + 8
        colh = max(colh, h)
    page.save(f'{OUT}/sheet_{n:02d}.png')
    print(len(sheets), 'graphics,', n + 1, 'sheets')


if __name__ == '__main__':
    main()
