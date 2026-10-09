# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat
import sys, json
root=Path('C:/Game/GameModel_3D');out=root/'renders'
def sheet(items,dest,width=420):
    pictures=[]
    for label,path in items:
        with Image.open(path) as im:
            im=im.convert('RGB');im.thumbnail((width,600));pictures.append((label,im.copy()))
    canvas=Image.new('RGB',(width*len(items),max(im.height for _,im in pictures)+40),(20,27,35));draw=ImageDraw.Draw(canvas)
    for i,(label,im) in enumerate(pictures):canvas.paste(im,(i*width,40));draw.text((i*width+12,12),label,fill='white')
    canvas.save(dest)
sheet([(label,out/f'waterfall_rel1_{key}.png') for label,key in [('Original','original'),('Refined current','refined_current'),('Waterfall Rel1 prototype','new')]],out/'waterfall_rel1_comparison.png')
sheet([(label,out/f'waterfall_rel1_closeup_{key}.png') for label,key in [('Spill lip','top'),('Main body','middle'),('Impact zone','base')]],out/'waterfall_rel1_closeups.png')
if '--video' in sys.argv:
    sys.path.insert(0,str(root/'.tools/water_video'));import imageio_ffmpeg
    reader=imageio_ffmpeg.read_frames(str(out/'waterfall_rel1_animation_preview.mp4'),pix_fmt='rgb24');meta=next(reader);w,h=meta['size'];frames=[];previous=None;deltas=[];flow_deltas=[]
    for count,raw in enumerate(reader,1):
        im=Image.frombytes('RGB',(w,h),raw)
        if count in [1,76,151,226,300]:
            path=out/f'waterfall_rel1_frame_{count:03d}.png';im.save(path);frames.append((f'Frame {count}',path))
        if previous is not None:
            deltas.append(sum(ImageStat.Stat(ImageChops.difference(previous,im)).mean)/3)
            box=(int(w*.47),int(h*.13),int(w*.78),int(h*.90))
            flow_deltas.append(sum(ImageStat.Stat(ImageChops.difference(previous.crop(box),im.crop(box))).mean)/3)
        previous=im
    sheet(frames,out/'waterfall_rel1_animation_frames.png',300)
    result={'frames':count,'metadata':meta,'mean_adjacent_rgb_difference':sum(deltas)/len(deltas),'mean_adjacent_flow_roi_rgb_difference':sum(flow_deltas)/len(flow_deltas)}
    (root/'reports/waterfall_rel1_video_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
