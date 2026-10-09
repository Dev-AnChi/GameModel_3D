# -*- coding: utf-8 -*-
"""Decode the actual H.264 preview and inspect temporal differences."""
from pathlib import Path
import sys, json, subprocess, re
from PIL import Image, ImageDraw, ImageChops, ImageStat
try:
    import numpy as np
except ImportError:
    np=None
ROOT=Path('C:/Game/GameModel_3D')
sys.path.insert(0,str(ROOT/'.tools/water_video'))
import imageio_ffmpeg
video=ROOT/'renders/water_animation_preview.mp4'
reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24')
meta=next(reader);w,h=meta['size'];frames=[];selected={0,75,150,225,299}
count=0;first=None;last=None;previous=None;diffs=[];full_diffs=[];profiles=[]
box=(int(w*.50),int(h*.15),int(w*.80),int(h*.90))
for count,raw in enumerate(reader,1):
    im=Image.frombytes('RGB',(w,h),raw)
    if np is not None:
        arr=np.frombuffer(raw,dtype=np.uint8).reshape(h,w,3)
        profiles.append(arr[int(h*.25):int(h*.80),int(w*.50):int(w*.78)].astype(np.float32).mean(axis=(1,2)))
    if count-1 in selected:frames.append((count,im.copy()))
    if first is None:first=im.copy()
    if previous is not None:
        # Flow region only: middle-right of the fixed preview camera.
        dif=ImageChops.difference(previous.crop(box),im.crop(box))
        diffs.append(sum(ImageStat.Stat(dif).mean)/3)
        full_diffs.append(sum(ImageStat.Stat(ImageChops.difference(previous,im)).mean)/3)
    previous=im;last=im
canvas=Image.new('RGB',(w*len(frames),h+30),(22,27,34));draw=ImageDraw.Draw(canvas)
for idx,(frame,im) in enumerate(frames):canvas.paste(im,(idx*w,30));draw.text((idx*w+10,10),f'Frame {frame}',fill='white')
canvas.save(ROOT/'renders/water_animation_frames.png')
loopdiff=sum(ImageStat.Stat(ImageChops.difference(last,first)).mean)/3
result={'decoded_frames':count,'metadata':meta,'flow_region_adjacent_mean_rgb_difference':sum(diffs)/len(diffs),
        'flow_region_adjacent_max_rgb_difference':max(diffs),'last_to_first_mean_rgb_difference':loopdiff,
        'full_frame_adjacent_mean_rgb_difference':sum(full_diffs)/len(full_diffs),
        'full_frame_adjacent_max_rgb_difference':max(full_diffs),
        'largest_adjacent_frame_steps':sorted(enumerate(full_diffs,1),key=lambda item:item[1],reverse=True)[:10],
        'loop_flow_region_mean_rgb_difference':sum(ImageStat.Stat(ImageChops.difference(last.crop(box),first.crop(box))).mean)/3,
        'note':'Last frame is t=299/300; first is t=0. They are expected to differ by one animation step, not to be identical.'}
loop_a=ROOT/'renders/water_loop_001.png';loop_b=ROOT/'renders/water_loop_301.png'
if loop_a.exists() and loop_b.exists():
    with Image.open(loop_a) as a,Image.open(loop_b) as b:
        result['rendered_frame_1_301_mean_rgb_difference']=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
        result['video_first_vs_rendered_first_mean_rgb_difference']=sum(ImageStat.Stat(ImageChops.difference(first,a.convert('RGB'))).mean)/3
if profiles:
    arr=np.asarray(profiles);arr-=arr.mean(axis=0)
    estimates=[]
    for idx in range(0,len(arr)-1,5):
        a=arr[idx];b=arr[idx+1];scores=[]
        for shift in range(-22,23):
            aa=a[max(0,-shift):min(len(a),len(a)-shift)]
            bb=b[max(0,shift):min(len(b),len(b)+shift)]
            denom=np.linalg.norm(aa)*np.linalg.norm(bb)
            scores.append(float(np.dot(aa,bb)/denom) if denom else -1)
        estimates.append(int(np.argmax(scores))-22)
    result['vertical_profile_motion_diagnostic']={'median_best_shift_px':float(np.median(estimates)),
        'positive_downward_fraction':sum(v>0 for v in estimates)/len(estimates),
        'note':'Temporal-mean-subtracted image profile cross-correlation; diagnostic, not a fluid velocity measurement.'}
probe=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-i',str(video),'-vf','showinfo','-an','-f','null','-'],
                     capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
result['h264_keyframe_indices_zero_based']=[int(v) for v in re.findall(r'n:\s*(\d+).*iskey:1',probe.stderr)]
(ROOT/'reports/water_video_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
