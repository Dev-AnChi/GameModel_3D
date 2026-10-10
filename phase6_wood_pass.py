# -*- coding: utf-8 -*-
"""Original directional oak PBR maps, grain UV mapping and neutral review."""
import bpy, numpy as np, math, os, json
from mathutils import Vector
ROOT=r'C:\Game\GameModel_3D\Wandering_Alchemist_v2'
TEX=os.path.join(ROOT,'Textures','Phase6_Wood')
OUT=os.path.join(ROOT,'renders','phase6_wood')
os.makedirs(TEX,exist_ok=True);os.makedirs(OUT,exist_ok=True)
scene=bpy.context.scene;cam=scene.camera
scene.render.filepath=os.path.join(OUT,'wood_before.png')
bpy.ops.render.render(write_still=True)
N=2048
u,v=np.meshgrid(np.linspace(0,1,N,dtype=np.float32),np.linspace(0,1,N,dtype=np.float32))

def image_map(name,rgb,data=False):
    rgba=np.ones((N,N,4),np.float32)
    if rgb.ndim==2:rgba[:,:,:3]=rgb[:,:,None]
    else:rgba[:,:,:3]=rgb
    im=bpy.data.images.new(name,width=N,height=N,alpha=False)
    im.colorspace_settings.name='Non-Color' if data else 'sRGB'
    im.pixels.foreach_set(rgba.ravel());im.file_format='PNG';im.filepath_raw=os.path.join(TEX,name+'.png');im.save()
    return im

families=[('Main_Oak',(.40,.245,.120),.48,7),('Dark_Walnut',(.21,.116,.061),.53,11),('Aged_Planks',(.33,.228,.139),.64,19),('Carved_Oak',(.43,.265,.136),.46,23),('Shelf_Oak',(.34,.187,.079),.50,31)]
mats={};checks=[]
for name,base,rough,seed in families:
    rng=np.random.default_rng(seed)
    # U is plank length. V bends growth layers into ribbons and small knots.
    bend=.014*np.sin(u*math.tau*1.4+seed)+.007*np.sin(u*math.tau*3.6+v*5)
    for k in range(2):
        ku,kv=rng.uniform(.17,.85),rng.uniform(.2,.8)
        bend+=.035*np.exp(-((u-ku)/.09)**2)*np.sin((v-kv)*13)
    phase=(v+bend)*math.tau*33
    growth=np.sin(phase)+.35*np.sin(phase*2.13+u*6)
    pores=np.power(np.clip(.5+.5*np.sin(phase*3.7+np.sin(u*31)),0,1),16)
    fine=np.sin(v*math.tau*205+u*18)*.012
    fibers=rng.normal(0,.010,(N,N)).astype(np.float32)
    grain=.10*growth-.08*pores+fine+fibers
    # Contact polish is restrained, separate from growth grain.
    border=np.exp(-v/.022)+np.exp(-(1-v)/.022)
    h=np.clip(.5+.055*growth-.022*pores+fine*.25+fibers*.14,0,1)
    rgb=np.empty((N,N,3),np.float32)
    for c in range(3):rgb[:,:,c]=np.clip(base[c]*(1+grain)+border*.018,0,1)
    r=np.clip(rough+.055*growth+.075*pores-.07*border, .32,.82)
    dy,dx=np.gradient(h)
    # Tangent normal: small pore relief, no displacement of the silhouette.
    normal=np.stack((-dx*105,-dy*105,np.ones_like(h)),axis=2)
    normal/=np.sqrt((normal**2).sum(axis=2))[:,:,None]
    normal=normal*.5+.5
    maps={k:image_map(name+'_'+k,a,k!='BaseColor') for k,a in [('BaseColor',rgb),('Roughness',r),('Normal',normal),('Height',h)]}
    m=bpy.data.materials.new('P6_'+name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    p=next(q for q in n if q.type=='BSDF_PRINCIPLED');p.inputs['Metallic'].default_value=0
    uv=n.new('ShaderNodeUVMap');uv.uv_map='Wood_Grain_UV'
    # Seeded object variation keeps a common material while avoiding identical grain repeats.
    for key,im in maps.items():
        node=n.new('ShaderNodeTexImage');node.name=key+'_Map';node.label=key;node.image=im;l.new(uv.outputs['UV'],node.inputs['Vector'])
        if key=='BaseColor':
            info=n.new('ShaderNodeObjectInfo');maprange=n.new('ShaderNodeMapRange');maprange.inputs['From Min'].default_value=0;maprange.inputs['From Max'].default_value=1;maprange.inputs['To Min'].default_value=.88;maprange.inputs['To Max'].default_value=1.10;l.new(info.outputs['Random'],maprange.inputs['Value'])
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;l.new(node.outputs['Color'],mix.inputs[1]);l.new(maprange.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        elif key=='Roughness':l.new(node.outputs['Color'],p.inputs['Roughness'])
        elif key=='Normal':
            norm=n.new('ShaderNodeNormalMap');norm.uv_map='Wood_Grain_UV';norm.inputs['Strength'].default_value=.50;l.new(node.outputs['Color'],norm.inputs['Color']);l.new(norm.outputs[0],p.inputs['Normal'])
        # Height stays available and saved; unused displacement prevents overworked surfaces.
    mats[name]=m
    checks.append({'material':m.name,'resolution':[N,N],'roughness_range':[float(r.min()),float(r.max())],'normal_max_length_error':float(np.abs(np.linalg.norm(normal*2-1,axis=2)-1).max()),'maps':{k:im.filepath_raw for k,im in maps.items()}})
    print('Maps saved:',name)

col=bpy.data.collections['REFERENCE_REBUILD']
oldwood={'A_Oak_Honey','A_Oak_Light','A_Walnut'}
assigned=[]
for obj in list(col.objects):
    slots=getattr(obj.data,'materials',[])
    if not any(m and m.name in oldwood for m in slots):continue
    # Convert the two wood curves to meshes for a portable UV-based shader.
    if obj.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');obj=bpy.context.object
    if obj.type!='MESH':continue
    family='Main_Oak'
    if any(m and m.name=='A_Walnut' for m in obj.data.materials):family='Dark_Walnut'
    elif obj.name.startswith(('Lower_Side','Far_Wall','Floor_Plank')):family='Aged_Planks'
    elif obj.name.startswith(('Interior_Display','Drawer')):family='Shelf_Oak'
    elif obj.name.startswith(('Rear_Arch','Arched_Door','Curved_Oak')):family='Carved_Oak'
    obj.data.materials.clear();obj.data.materials.append(mats[family])
    me=obj.data
    uv=me.uv_layers.get('Wood_Grain_UV') or me.uv_layers.new(name='Wood_Grain_UV')
    coords=np.array([tuple(q.co) for q in me.vertices],dtype=float)
    if len(coords)<3:continue
    center=coords.mean(axis=0)
    eigenvals,axes=np.linalg.eigh(np.cov((coords-center).T))
    longaxis=axes[:,-1];cross1=axes[:,-2];cross2=axes[:,0]
    along=(coords-center)@longaxis;across=(coords-center)@cross1;other=(coords-center)@cross2
    length=max(float(np.ptp(along)),.001);width=max(float(np.ptp(across)),.001);thick=max(float(np.ptp(other)),.001)
    # Rims need tangential grain along the circumference, not the global X axis.
    rim=obj.name.startswith('Curved_Oak_Felloe')
    if rim:
        pivot=obj.parent.location;angle=np.unwrap(np.arctan2(coords[:,2]-pivot.z,coords[:,0]-pivot.x));amin,arange=float(angle.min()),max(float(np.ptp(angle)),.001)
    offset=(sum(ord(q) for q in obj.name)%73)/73*.6
    for polygon in me.polygons:
        endgrain=abs(Vector(longaxis).dot(polygon.normal))>.80
        for li in polygon.loop_indices:
            vi=me.loops[li].vertex_index
            if rim:
                radial=math.hypot(coords[vi,0]-pivot.x,coords[vi,2]-pivot.z)
                U=(angle[vi]-amin)/arange;V=(radial-.665)/.125
            elif endgrain:
                U=(across[vi]-across.min())/width;V=(other[vi]-other.min())/thick
            else:
                U=(along[vi]-along.min())/length
                V=(across[vi]-across.min())/width if abs(Vector(cross2).dot(polygon.normal))>.5 else (other[vi]-other.min())/thick
            uv.data[li].uv=(U,V*.78+offset)
    assigned.append({'object':obj.name,'family':family,'uv':'Wood_Grain_UV','faces':len(me.polygons)})

# Render same white studio as before for a direct comparison, plus material detail views.
views={'hero':((-8,-11,7),(-.6,0,2.1),9.8),'rear':((9,-10,6),(-.6,0,2.1),9.8),'side':((0,-13,3.4),(-.6,0,2.1),9.8),'wood_closeup':((-2.2,-5,3.15),(-.6,-1.2,1.95),3.1),'wheel_closeup':((-2.8,-5,1.5),(-1.95,-1.48,.84),2.2),'rear_door':((7,-2,3.4),(2.8,0,2.4),3.6)}
for name,(pos,target,size) in views.items():
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size
    scene.render.filepath=os.path.join(OUT,'wood_'+name+'.png');bpy.ops.render.render(write_still=True)
cam.location=(-8,-11,7);cam.rotation_euler=(Vector((-.6,0,2.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=9.8
with open(os.path.join(ROOT,'reports','Phase6_Wood_Map_QA.json'),'w',encoding='utf-8') as f:json.dump({'maps':checks,'assignments':assigned},f,indent=2,ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Blender','Wandering_Alchemist_Phase6A_Wood.blend'))
print('Wood objects assigned:',len(assigned),'Texture files:',len(checks)*4)
