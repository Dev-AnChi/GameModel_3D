# -*- coding: utf-8 -*-
"""Compose only actual Blender renders into labeled comparison sheets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path('C:/Game/GameModel_3D/renders')
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28)


def sheet(pairs,filename,width=1000):
    rows=[]
    for label,before,after in pairs:
        images=[Image.open(ROOT/name).convert('RGB') for name in (before,after)]
        height=max(round(im.height*width/im.width) for im in images)
        row=Image.new('RGB',(width*2,height+60),(30,34,37))
        draw=ImageDraw.Draw(row)
        for index,(im,suffix) in enumerate(zip(images,['TRƯỚC','SAU'])):
            im.thumbnail((width,height),Image.Resampling.LANCZOS)
            row.paste(im,(index*width+(width-im.width)//2,60))
            draw.text((index*width+24,14),label+' · '+suffix,font=FONT,fill=(239,232,215))
        rows.append(row)
    canvas=Image.new('RGB',(width*2,sum(r.height for r in rows)),(30,34,37))
    y=0
    for row in rows:canvas.paste(row,(0,y));y+=row.height
    canvas.save(ROOT/filename)
    print(filename,canvas.size)


if __name__=='__main__':
    sheet([(label,kind+'_material_before.png',kind+'_material.png') for label,kind in [('Đá limestone','rock'),('Gỗ honey oak','wood'),('Vải linen','fabric')]],'material_before_after.png',900)
    if (ROOT/'fabric_detail_final.png').exists():
        sheet([('Chi tiết sợi vải','fabric_detail_before.png','fabric_detail_final.png')],'fabric_detail_before_after.png',900)
    complete=[('Phòng khách','living_room'),('Vách đá hữu cơ','organic_cliff'),('Vườn mái','rooftop'),('Phòng ngủ','bedroom')]
    if all((ROOT/(kind+'_material_final.png')).exists() for _,kind in complete):
        sheet([(label,kind+'_material_before.png',kind+'_material_final.png') for label,kind in complete],'material_scene_before_after.png',900)
    if (ROOT/'overview_material_final.png').exists():
        sheet([('Toàn cảnh','overview_material_before.png','overview_material_final.png')],'overview_material_before_after.png',720)
