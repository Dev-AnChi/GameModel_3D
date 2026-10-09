# -*- coding: utf-8 -*-
"""Local-only Rel1 study: never overwrite a source master."""
import bpy, math, json
from mathutils import Vector
NS=bpy.app.driver_namespace
ROOT='C:/Game/GameModel_3D'
ASSET=ROOT+'/textures/water/waterfall_rel1/'

def mathnode(n,l,op,a=None,b=None):
    q=n.new('ShaderNodeMath');q.operation=op
    for i,v in enumerate([a,b]):
        if v is None:continue
        if isinstance(v,(int,float)):q.inputs[i].default_value=v
        else:l.new(v,q.inputs[i])
    return q.outputs[0]

def frames(n,l,uv,kind='flow',phase=0):
    count=11 if kind=='flow' else 6
    image=bpy.data.images.load(ASSET+kind+'_atlas.png',check_existing=True);image.pack()
    time=n.new('ShaderNodeValue');time.label='Interpolated source frames: 10-second periodic clock'
    time.outputs[0].driver_add('default_value').driver.expression=f'((frame-1)*{count*7}/300.0+{phase})%{count}'
    index=mathnode(n,l,'FLOOR',time.outputs[0]);frac=mathnode(n,l,'FRACT',time.outputs[0])
    nxt=mathnode(n,l,'MODULO',mathnode(n,l,'ADD',index,1),count)
    sep=n.new('ShaderNodeSeparateXYZ');l.new(uv,sep.inputs[0])
    u=mathnode(n,l,'MULTIPLY_ADD',sep.outputs['X'],.996)
    # Padding remains inside each source cell; never interpolates adjacent frames spatially.
    u.node.inputs[2].default_value=.002
    cols=[]
    for idx in [index,nxt]:
        x=mathnode(n,l,'DIVIDE',mathnode(n,l,'ADD',u,idx),count)
        combine=n.new('ShaderNodeCombineXYZ');l.new(x,combine.inputs['X']);l.new(sep.outputs['Y'],combine.inputs['Y'])
        tex=n.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';l.new(combine.outputs[0],tex.inputs[0]);cols.append(tex.outputs['Color'])
    mix=n.new('ShaderNodeMixRGB');l.new(frac,mix.inputs[0]);l.new(cols[0],mix.inputs[1]);l.new(cols[1],mix.inputs[2])
    return mix.outputs[0]

def watermat(name,side=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='DITHERED';m.use_backface_culling=False
    m['source']='waterfall_tex0.jpg through waterfall_tex10.jpg';m['license_warning']='Unknown original GIF author; public-domain status NOT guaranteed by readme.'
    n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    uv=n.new('ShaderNodeTexCoord');col=frames(n,l,uv.outputs['UV'],phase=3.2 if side else 0)
    bw=n.new('ShaderNodeRGBToBW');l.new(col,bw.inputs[0])
    density=n.new('ShaderNodeMapRange');l.new(bw.outputs[0],density.inputs['Value']);density.inputs['From Min'].default_value=.24;density.inputs['From Max'].default_value=.76;density.inputs['To Min'].default_value=.04;density.inputs['To Max'].default_value=.58;density.clamp=True
    nu=n.new('ShaderNodeVectorMath');nu.operation='MULTIPLY';nu.inputs[1].default_value=(2,7,1);l.new(uv.outputs['UV'],nu.inputs[0])
    move=n.new('ShaderNodeVectorMath');move.operation='ADD';l.new(nu.outputs[0],move.inputs[0]);move.inputs[1].driver_add('default_value',1).driver.expression='(frame-1)*19/300.0'
    tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images['normal.png'];l.new(move.outputs[0],tx.inputs[0])
    normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.11;l.new(tx.outputs['Color'],normal.inputs['Color'])
    a=n.new('ShaderNodeBsdfPrincipled');a.inputs['Base Color'].default_value=(.012,.46,.56,1);a.inputs['Roughness'].default_value=.20;a.inputs['IOR'].default_value=1.333;a.inputs['Transmission Weight'].default_value=.27 if not side else .62;a.inputs['Emission Color'].default_value=(.008,.26,.32,1);a.inputs['Emission Strength'].default_value=.16;l.new(normal.outputs[0],a.inputs['Normal'])
    b=n.new('ShaderNodeBsdfPrincipled');b.inputs['Base Color'].default_value=(.72,.96,1,1);b.inputs['Roughness'].default_value=.26;b.inputs['Emission Color'].default_value=(.4,.7,.77,1);b.inputs['Emission Strength'].default_value=.11;l.new(normal.outputs[0],b.inputs['Normal'])
    mix=n.new('ShaderNodeMixShader');l.new(density.outputs[0],mix.inputs[0]);l.new(a.outputs[0],mix.inputs[1]);l.new(b.outputs[0],mix.inputs[2])
    opacity=mathnode(n,l,'MULTIPLY_ADD',density.outputs[0],.40 if side else .28);opacity.node.inputs[2].default_value=.48 if side else .73
    tr=n.new('ShaderNodeBsdfTransparent');alpha=n.new('ShaderNodeMixShader');l.new(opacity,alpha.inputs[0]);l.new(tr.outputs[0],alpha.inputs[1]);l.new(mix.outputs[0],alpha.inputs[2])
    out=n.new('ShaderNodeOutputMaterial');l.new(alpha.outputs[0],out.inputs[0])
    for i,q in enumerate(n):q.location=(i//7*220-1000,-(i%7)*150)
    return m

def foammat(kind):
    m=bpy.data.materials.new('REL1 | '+kind+' impact mask');m.use_nodes=True;m.surface_render_method='DITHERED'
    n=m.node_tree.nodes;n.clear();l=m.node_tree.links;uv=n.new('ShaderNodeTexCoord')
    if kind=='ripple':col=frames(n,l,uv.outputs['UV'],kind='ripple',phase=1.7)
    else:
        tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(ASSET+'foam_particle.png',check_existing=True);tx.image.pack();l.new(uv.outputs['UV'],tx.inputs[0]);col=tx.outputs['Alpha']
    if kind=='ripple':
        bw=n.new('ShaderNodeRGBToBW');l.new(col,bw.inputs[0]);col=bw.outputs[0]
    b=n.new('ShaderNodeBsdfPrincipled');b.inputs['Base Color'].default_value=(.75,.96,1,1);b.inputs['Roughness'].default_value=.30;b.inputs['Emission Color'].default_value=(.4,.66,.72,1);b.inputs['Emission Strength'].default_value=.15
    tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(col,mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(b.outputs[0],mix.inputs[2]);o=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],o.inputs[0]);return m

def setup():
    s=NS['ai_scene'];bpy.context.window.scene=s;s.frame_set(75)
    c=bpy.data.collections.new('REL1 | Waterfall_03 local asset study');s.collection.children.link(c);NS['rel_collection']=c
    body=watermat('REL1 | Turquoise aerated interpolated flow');side=watermat('REL1 | Clear edge flow',True);foam=foammat('foam');ripple=foammat('ripple')
    for source in NS['ai_baseline']:
        if NS['ai_before_visibility'][source.name]:continue
        if source.name in ['R39 short separated stream 1','R39 short separated stream 3']:continue
        o=source.copy();o.data=source.data.copy();o.name=source.name.replace('R39','REL1',1);c.objects.link(o)
        o['source_geometry']=source.name
        if 'mass' in source.name:
            if o.data.shape_keys:o.shape_key_clear()
            verts=o.data.vertices
            centers=[sum((v.co for v in verts[i*16:(i+1)*16]),Vector())/16 for i in range(65)]
            cross=Vector((.818,.575,0));normal=Vector((.575,-.818,0))
            for i in range(65):
                sm=sum((centers[j] for j in range(max(0,i-2),min(65,i+3))),Vector())/(min(65,i+3)-max(0,i-2)) if 8<i<59 else centers[i]
                for k in range(16):
                    v=verts[i*16+k];d=v.co-centers[i]
                    v.co=sm+cross*d.dot(cross)*(1.24 if 'main' in o.name else .75)+normal*d.dot(normal)*.83+Vector((0,0,d.z*.6))
            o.data.materials.clear();o.data.materials.append(body if 'main' in o.name else side)
            basis=o.shape_key_add(name='Basis');pulse=o.shape_key_add(name='Subtle traveling volume pulse')
            for i,p in enumerate(pulse.data):
                t=(i//16)/64;p.co+=normal*(.013*math.sin(t*19)*math.sin(math.pi*t))
            pulse.driver_add('value').driver.expression='.5+.5*sin(2*pi*(frame-1)*3/300)'
        elif 'short separated' in o.name or 'splash' in o.name:
            o.data.materials.clear();o.data.materials.append(side)
        elif 'foam patch' in o.name:
            o.data.materials.clear();o.data.materials.append(foam)
            uv=o.data.uv_layers.active or o.data.uv_layers.new(name='ImpactUV')
            xs=[v.co.x for v in o.data.vertices];ys=[v.co.y for v in o.data.vertices]
            for loop in o.data.loops:
                p=o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((p.x-min(xs))/(max(xs)-min(xs)),(p.y-min(ys))/(max(ys)-min(ys)))
    # Reuse safe terrain contact footprint, but animate actual six-frame ring texture.
    patch=next(o for o in c.objects if 'foam patch' in o.name)
    ring=patch.copy();ring.data=patch.data.copy();ring.name='REL1 | Six-frame impact ripples';c.objects.link(ring)
    for v in ring.data.vertices:v.co.z+=.014
    ring.data.materials[0]=ripple
    NS['rel_mats']=[body,side,foam,ripple]
    # User-provided cloud background, centered crop, no changes to world lighting.
    g=bpy.data.node_groups.new('REL1 | Reference cloud background','CompositorNodeTree');g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    n=g.nodes;l=g.links;rl=n.new('CompositorNodeRLayers');rl.scene=s;im=n.new('CompositorNodeImage');im.image=bpy.data.images.load(ROOT+'/textures/water/integration/Catmosphere_Cloud_Islands_Background.png',check_existing=True);im.image.pack()
    scale=n.new('CompositorNodeScale');scale.inputs['X'].default_value=s.render.resolution_x/941;scale.inputs['Y'].default_value=s.render.resolution_x/941;l.new(im.outputs[0],scale.inputs['Image'])
    over=n.new('CompositorNodeAlphaOver');l.new(scale.outputs[0],over.inputs['Background']);l.new(rl.outputs['Image'],over.inputs['Foreground']);out=n.new('NodeGroupOutput');l.new(over.outputs[0],out.inputs['Image']);s.compositing_node_group=g;s.render.film_transparent=True
    NS['rel_background']=g
    variant('new');print('REL_SETUP',len(c.objects))

def variant(mode):
    for o in NS['ai_baseline']:o.hide_render=NS['ai_before_visibility'][o.name] if mode=='refined' else True
    for o in NS['rel_collection'].objects:o.hide_render=mode!='new'
    for name in ['Waterfall_03','Organic cascade foam 2','Organic impact foam 2']:bpy.data.objects[name].hide_render=mode!='original'

def render(mode,name,camera=None):
    s=NS['ai_scene'];bpy.context.window.scene=s;variant(mode);s.frame_set(75);s.camera=camera or NS['ai_camera'];s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=ROOT+'/renders/'+name;bpy.ops.render.render(write_still=True,scene=s.name);variant('new');s.camera=NS['ai_camera']

NS['rel_api']={'setup':setup,'variant':variant,'render':render}
