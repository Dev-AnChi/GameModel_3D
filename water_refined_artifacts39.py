# -*- coding: utf-8 -*-
"""Contact sheets and QA from actual Blender renders, never synthetic views."""
from pathlib import Path
import sys, json, hashlib
from PIL import Image, ImageDraw, ImageChops, ImageStat
ROOT=Path('C:/Game/GameModel_3D');OUT=ROOT/'renders'
sys.path.insert(0,str(ROOT/'.tools/water_video'))
import imageio_ffmpeg

def sheet(items, destination, width=480):
    ims=[]
    for label,path in items:
        with Image.open(path) as source:
            im=source.convert('RGB');im.thumbnail((width,650));ims.append((label,im))
    height=max(im.height for _,im in ims)+36
    canvas=Image.new('RGB',(width*len(ims),height),(22,27,34));draw=ImageDraw.Draw(canvas)
    for i,(label,im) in enumerate(ims):
        canvas.paste(im,(width*i+(width-im.width)//2,36));draw.text((width*i+14,12),label,fill='white')
    canvas.save(destination)

sheet([(label,OUT/file) for label,file in [
    ('Original - Frame 75','waterfall_original_refine_compare.png'),
    ('Pass A - Frame 75','waterfall_pass_a_refine_compare.png'),
    ('Pass A Refined - Frame 75','waterfall_refined.png')]],OUT/'waterfall_refined_three_way.png')
sheet([(label,OUT/f'waterfall_refined_closeup_{key}.png') for label,key in
       [('Spill lip','top'),('Main water body','middle'),('Impact foam and splash','base')]],OUT/'waterfall_refined_closeups.png')
if '--stills-only' in sys.argv:
    print('Actual-render contact sheets refreshed.');sys.exit(0)

video=OUT/'waterfall_refined_animation_preview.mp4'
if video.exists():
    reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24');meta=next(reader);w,h=meta['size']
    selected=[];previous=None;diffs=[];count=0
    for count,raw in enumerate(reader,1):
        im=Image.frombytes('RGB',(w,h),raw)
        if count in [1,76,151,226,300]:
            path=OUT/f'water_refined_frame_{count:03d}.png';im.save(path);selected.append((f'Frame {count}',path))
        if previous is not None:
            box=(int(w*.48),int(h*.15),int(w*.82),int(h*.9))
            diffs.append(sum(ImageStat.Stat(ImageChops.difference(previous.crop(box),im.crop(box))).mean)/3)
        previous=im
    sheet(selected,OUT/'waterfall_refined_animation_frames.png',width=360)
    with Image.open(OUT/'water_refined_loop_001.png') as a,Image.open(OUT/'water_refined_loop_301.png') as b:
        loopdiff=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
    result={'decoded_frames':count,'metadata':meta,'mean_adjacent_flow_rgb_difference':sum(diffs)/len(diffs),
            'render_frame_1_301_mean_rgb_difference':loopdiff,
            'pass_a_sha256':hashlib.sha256((ROOT/'Catmosphere_Water_Master.blend').read_bytes()).hexdigest(),
            'note':'Metrics verify the exported video; visual approval remains required. Frame 300 is one step before frame 301.'}
    (ROOT/'reports/water_refined_video_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
else:print('Contact sheets created; refined video is not available yet.')
