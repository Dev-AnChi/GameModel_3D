# -*- coding: utf-8 -*-
"""Download selected CC0 maps from official Poly Haven API manifests."""
import urllib.request, json, pathlib, hashlib
from PIL import Image
ROOT=pathlib.Path(r'C:\Game\GameModel_3D\Wandering_Alchemist_v2')
OUT=ROOT/'textures'/'downloaded';OUT.mkdir(parents=True,exist_ok=True)
report=[]
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'WanderingAlchemistMaterialReview/1.0'})
    with urllib.request.urlopen(req,timeout=60) as response:
        assert response.status==200
        return response.read(),response.status
for asset in ('oak_veneer_01','rough_linen','metal_plate_02'):
    meta=json.loads(get('https://api.polyhaven.com/info/'+asset)[0])
    manifest=json.loads(get('https://api.polyhaven.com/files/'+asset)[0])
    entry={'id':asset,'name':meta['name'],'authors':meta.get('authors',{}),'page':'https://polyhaven.com/a/'+asset,'license':'CC0','license_url':'https://polyhaven.com/license','download_date':'2026-10-10','files':{}}
    for channel in ('Diffuse','Rough','nor_gl'):
        formats=manifest[channel]['2k'];fmt='png' if channel=='nor_gl' else 'jpg'
        record=formats[fmt];url=record['url']
        assert urllib.parse.urlparse(url).hostname=='dl.polyhaven.org'
        data,status=get(url)
        assert len(data)==record['size'],(asset,channel,'size mismatch')
        digest=hashlib.md5(data).hexdigest()
        assert digest==record['md5'],(asset,channel,'hash mismatch')
        path=OUT/asset/pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name
        path.parent.mkdir(exist_ok=True);path.write_bytes(data)
        with Image.open(path) as im:
            im.load();width,height=im.size;imageformat=im.format
        entry['files'][channel]={'path':str(path),'url':url,'http_status':status,'bytes':len(data),'md5':digest,'resolution':[width,height],'format':imageformat}
        print(asset,channel,len(data),width,height,flush=True)
    report.append(entry)
with (OUT/'verified_manifest.json').open('w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('Verified sets:',len(report))
