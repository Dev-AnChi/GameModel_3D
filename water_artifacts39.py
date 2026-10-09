# -*- coding: utf-8 -*-
"""Validate downloaded assets and compose actual Blender renders; never synthesize renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat
import hashlib, json
ROOT=Path('C:/Game/GameModel_3D')
records=[]
for p in sorted((ROOT/'textures/water').rglob('*.png')):
    with Image.open(p) as im:
        im.load()
        rgb=im.convert('RGB');w,h=rgb.size
        top=rgb.crop((0,0,w,1));bottom=rgb.crop((0,h-1,w,h));near=rgb.crop((0,1,w,2))
        records.append({'path':str(p.relative_to(ROOT)), 'size':im.size,
                        'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        'vertical_wrap_edge_mean_rgb_difference':sum(ImageStat.Stat(ImageChops.difference(top,bottom)).mean)/3,
                        'adjacent_top_rows_mean_rgb_difference':sum(ImageStat.Stat(ImageChops.difference(top,near)).mean)/3})
(ROOT/'reports/water_asset_validation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
canvas=Image.new('RGB',(1040,725),(24,31,39));draw=ImageDraw.Draw(canvas)
for x,filename,label in [(10,'waterfall_before.png','BEFORE'),(530,'waterfall_after.png','PASS A - PROTOTYPE')]:
    with Image.open(ROOT/'renders'/filename) as im:
        im=im.convert('RGB');im.thumbnail((500,675));canvas.paste(im,(x+(500-im.width)//2,40))
    draw.text((x+15,15),label,fill='white')
canvas.save(ROOT/'renders/waterfall_before_after.png')
print(json.dumps({'validated_images':len(records),'comparison':'renders/waterfall_before_after.png'},ensure_ascii=False))
