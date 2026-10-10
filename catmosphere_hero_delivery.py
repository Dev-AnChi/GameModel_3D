# -*- coding: utf-8 -*-
"""Assemble comparison sheets from real Blender renders; never alter scene content."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'renders'
FONT = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 26)


def panel(path, label, size):
    src = Image.open(path).convert('RGB')
    src.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (size[0], size[1] + 52), '#edf2f4')
    canvas.paste(src, ((size[0] - src.width) // 2, 52 + (size[1] - src.height) // 2))
    ImageDraw.Draw(canvas).text((18, 12), label, font=FONT, fill='#20343c')
    return canvas


def main():
    a = panel(OUT / 'catmosphere_hero_before.png', 'Before — source scene', (756, 1344))
    b = panel(OUT / 'catmosphere_hero_final.png', 'After — hero beauty pass', (756, 1344))
    comparison = Image.new('RGB', (1512, 1396), '#edf2f4')
    comparison.paste(a, (0, 0)); comparison.paste(b, (756, 0))
    comparison.save(OUT / 'catmosphere_hero_before_after.png')
    levels = [('rooftop', 'Rooftop garden'), ('lounge', 'Living / lounge'),
              ('bedroom', 'Bedroom'), ('dining', 'Dining terrace'), ('beach', 'Beach / pool dock')]
    sheet = Image.new('RGB', (1440, 1064), '#edf2f4')
    for index, (key, label) in enumerate(levels):
        tile = panel(OUT / f'catmosphere_hero_{key}.png', label, (480, 480))
        sheet.paste(tile, ((index % 3) * 480, (index // 3) * 532))
    sheet.save(OUT / 'catmosphere_hero_level_closeups.png')
    for path in sorted(OUT.glob('catmosphere_hero_*.png')):
        with Image.open(path) as im:
            im.verify()
        print(path.name, path.stat().st_size)


if __name__ == '__main__':
    main()
