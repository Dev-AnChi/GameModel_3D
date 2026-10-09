# -*- coding: utf-8 -*-
"""Verify delivered PNGs, UTF-8/NFC reports, and actual material differences."""
import json
import unicodedata
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT=Path('C:/Game/GameModel_3D')
required=['material_before_after','wood_material','rock_material','fabric_material','overview_material_final','living_room_material_final','organic_cliff_material_final','rooftop_material_final','bedroom_material_final']
results={}
for name in required:
    path=ROOT/'renders'/(name+'.png')
    with Image.open(path) as im:
        im.load()
        variance=ImageStat.Stat(im.convert('RGB').resize((200,200))).var
        if max(variance)<1:raise RuntimeError('Blank render '+name)
        results[name]={'size':list(im.size),'bytes':path.stat().st_size,'variance':variance}
differences={}
for kind in ['wood','rock','fabric','living_room','organic_cliff','rooftop','bedroom','overview']:
    a=Image.open(ROOT/'renders'/(kind+'_material_before.png')).convert('RGB')
    after=kind+'_material'+('' if kind in ['wood','rock','fabric'] else '_final')+'.png'
    b=Image.open(ROOT/'renders'/after).convert('RGB')
    if b.size!=a.size:b=b.resize(a.size,Image.Resampling.LANCZOS)
    diff=ImageChops.difference(a,b)
    mean=ImageStat.Stat(diff).mean
    differences[kind]={'mean_absolute_rgb_8bit':mean,'same_resolution':Image.open(ROOT/'renders'/after).size==a.size}
    if max(mean)<.05:raise RuntimeError('No meaningful pixel change '+kind)
for name in ['material_audit.md','texture_sources.md']:
    text=(ROOT/'reports'/name).read_text(encoding='utf-8')
    if unicodedata.normalize('NFC',text)!=text:raise RuntimeError('NFC check failed '+name)
    if '\ufffd' in text:raise RuntimeError('Replacement character '+name)
data={'renders':results,'before_after_difference':differences,'reports_utf8_nfc':True}
(ROOT/'reports/material_artifact_validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'renders':len(results),'utf8_nfc':True,'mean_differences':{k:round(sum(v['mean_absolute_rgb_8bit'])/3,3) for k,v in differences.items()}},ensure_ascii=False))
