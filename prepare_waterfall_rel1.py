# -*- coding: utf-8 -*-
"""Read asset data and pack source frames without repainting them."""
from pathlib import Path
from PIL import Image, ImageDraw
import struct, json, hashlib
root = Path('textures/water/waterfall_rel1')
for stem, names in [('flow', [f'waterfall_tex{i}.jpg' for i in range(11)]),
                    ('ripple', [f'waves_concent_tex{i}.png' for i in range(1, 7)])]:
    atlas = Image.new('RGB', (256 * len(names), 256))
    for i, name in enumerate(names):
        with Image.open(root / name) as im:
            im.load(); atlas.paste(im.convert('RGB'), (256*i, 0))
    atlas.save(root / f'{stem}_atlas.png')
data = (root/'waterfall.b3d').read_bytes()
chunks=[]
def scan(start,end,level=0):
    p=start
    while p+8<=end:
        tag=data[p:p+4].decode('ascii',errors='replace'); size=struct.unpack_from('<I',data,p+4)[0]
        if p+8+size>end: break
        chunks.append({'tag':tag,'bytes':size,'level':level})
        q=p+8
        if tag=='NODE':
            z=data.index(b'\0',q,p+8+size); scan(z+1+40,p+8+size,level+1)
        elif tag=='MESH': scan(q+4,p+8+size,level+1)
        p+=8+size
scan(12,len(data))
report={'b3d_magic':data[:4].decode('ascii'),'b3d_version':struct.unpack_from('<I',data,8)[0],
        'b3d_chunks':chunks,'files':[{ 'name':f.name,'bytes':f.stat().st_size,
        'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in root.iterdir() if f.is_file()]}
(root/'inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
