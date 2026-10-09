# -*- coding: utf-8 -*-
"""Adapt the downloaded CC0 Toon Waterfall to Waterfall_03 using live Blender MCP."""
import bpy, bmesh, math, hashlib, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT='C:/Game/GameModel_3D';NS=bpy.app.driver_namespace

def signature(o):
    return hashlib.sha256(repr([o.name,o.type,[list(r) for r in o.matrix_world],
        [tuple(v.co) for v in o.data.vertices] if o.type=='MESH' else o.data.name,
        [m.name if m else None for m in getattr(o.data,'materials',[])]]).encode('utf-8')).hexdigest()

def enum(o,prop,value):
    values=[i.identifier for i in o.bl_rna.properties[prop].enum_items]
    if values and value not in values:raise ValueError((prop,value,values))
    setattr(o,prop,value)

def init():
    s=bpy.data.scenes['Scene'];bpy.context.window.scene=s;s.frame_set(75)
    NS['ai_protected']={o.name:signature(o) for o in s.objects};NS['ai_scene']=s;NS['ai_camera']=s.camera
    NS['ai_baseline']=list(bpy.data.collections['R39 | Waterfall_03 Refined'].objects)
    NS['ai_before_visibility']={o.name:o.hide_render for o in NS['ai_baseline']}
    c=bpy.data.collections.new('AI | Waterfall_03 Asset Prototype');s.collection.children.link(c);NS['ai_collection']=c
    NS['ai_cross']=Vector((.818,.575,0));NS['ai_normal']=Vector((.575,-.818,0))
    image=bpy.data.images.load(ROOT+'/textures/water/integration/doodlebuilt_waterfall_fx.png',check_existing=True);image.pack();NS['ai_flow_image']=image
    NS['ai_trees']=NS['r39_static']
    print('AI_INITIALIZED',len(NS['ai_protected']))

def background():
    s=NS['ai_scene'];group=bpy.data.node_groups.new('AI | Catmosphere cloud-island background','CompositorNodeTree')
    group.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    n=group.nodes;l=group.links
    render=n.new('CompositorNodeRLayers');render.scene=s;render.location=(-450,100)
    image=n.new('CompositorNodeImage');image.image=bpy.data.images.load(ROOT+'/textures/water/integration/Catmosphere_Cloud_Islands_Background.png',check_existing=True);image.image.pack();image.location=(-450,-150)
    scale=n.new('CompositorNodeScale');enum(scale,'space','RENDER_SIZE');enum(scale,'frame_method','CROP');scale.location=(-220,-150);l.new(image.outputs['Image'],scale.inputs['Image'])
    over=n.new('CompositorNodeAlphaOver');over.location=(0,80);over.inputs[0].default_value=1;l.new(scale.outputs['Image'],over.inputs[1]);l.new(render.outputs['Image'],over.inputs[2])
    out=n.new('NodeGroupOutput');out.location=(220,80);l.new(over.outputs['Image'],out.inputs['Image'])
    s.compositing_node_group=group;s.render.film_transparent=True
    NS['ai_background_group']=group
    print('BACKGROUND_IMAGE_PACKED')

def material(name,ridge=False,shape=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;enum(m,'surface_render_method','DITHERED');m.use_backface_culling=False
    n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    def new(t):return n.new(t)
    uv=new('ShaderNodeTexCoord');uv.location=(-950,0)
    add=new('ShaderNodeVectorMath');enum(add,'operation','ADD');l.new(uv.outputs['UV'],add.inputs[0]);add.inputs[1].default_value=(0,0,0)
    add.inputs[1].driver_add('default_value',1).driver.expression='(frame-1)*'+('21' if ridge else '15')+'/300.0'
    tex=new('ShaderNodeTexImage');tex.image=NS['ai_flow_image'];enum(tex,'extension','REPEAT');l.new(add.outputs[0],tex.inputs['Vector'])
    bw=new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0])
    density=new('ShaderNodeMapRange');density.clamp=True;density.inputs['From Min'].default_value=.115;density.inputs['From Max'].default_value=.54;l.new(bw.outputs[0],density.inputs['Value'])
    normaluv=new('ShaderNodeVectorMath');enum(normaluv,'operation','MULTIPLY');normaluv.inputs[1].default_value=(2.5,5,1);l.new(uv.outputs['UV'],normaluv.inputs[0])
    flow=new('ShaderNodeVectorMath');enum(flow,'operation','ADD');l.new(normaluv.outputs[0],flow.inputs[0]);flow.inputs[1].driver_add('default_value',1).driver.expression='(frame-1)*23/300.0'
    texnormal=new('ShaderNodeTexImage');texnormal.image=bpy.data.images['normal.png'];enum(texnormal,'extension','REPEAT');l.new(flow.outputs[0],texnormal.inputs[0])
    nm=new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.19;l.new(texnormal.outputs['Color'],nm.inputs['Color'])
    water=new('ShaderNodeBsdfPrincipled');water.inputs['Base Color'].default_value=(.025,.43,.55,1);water.inputs['Roughness'].default_value=.12;water.inputs['IOR'].default_value=1.333;water.inputs['Transmission Weight'].default_value=.48
    water.inputs['Emission Color'].default_value=(.025,.35,.44,1);water.inputs['Emission Strength'].default_value=.10;l.new(nm.outputs[0],water.inputs['Normal'])
    foam=new('ShaderNodeBsdfPrincipled');foam.inputs['Base Color'].default_value=(.78,.96,1,1);foam.inputs['Roughness'].default_value=.25;foam.inputs['IOR'].default_value=1.333;foam.inputs['Emission Color'].default_value=(.45,.68,.75,1);foam.inputs['Emission Strength'].default_value=.13;l.new(nm.outputs[0],foam.inputs['Normal'])
    mix=new('ShaderNodeMixShader');l.new(density.outputs[0],mix.inputs[0]);l.new(water.outputs[0],mix.inputs[1]);l.new(foam.outputs[0],mix.inputs[2])
    tr=new('ShaderNodeBsdfTransparent');opacity=new('ShaderNodeMath');enum(opacity,'operation','MULTIPLY');l.new(tex.outputs['Alpha'],opacity.inputs[0]);opacity.inputs[1].default_value=.48 if ridge else .94
    alpha=new('ShaderNodeMixShader');l.new(opacity.outputs[0],alpha.inputs[0]);l.new(tr.outputs[0],alpha.inputs[1]);l.new(mix.outputs[0],alpha.inputs[2]);out=new('ShaderNodeOutputMaterial');l.new(alpha.outputs[0],out.inputs[0])
    if shape:
        matte=new('ShaderNodeBsdfPrincipled');matte.inputs['Base Color'].default_value=(.035,.45,.50,1);matte.inputs['Roughness'].default_value=.36;l.new(matte.outputs[0],out.inputs[0])
    for i,q in enumerate(n):q.location=(int(i/5)*230-900,-(i%5)*210)
    m['asset_source']='https://opengameart.org/content/toon-waterfall';m['asset_license']='CC0';return m

def center(t):
    t=max(0,min(1,t));base=NS['r39_source_paths'][0]
    i=min(63,int(t*64));f=t*64-i;p=base[i].lerp(base[i+1],f)
    p.y-=.48*math.sin(math.pi*t)**.8+.09
    p.x=max(p.x,4.90+.27*t)
    # The same clearance strategy is applied to asset-derived geometry, not to scenery.
    half=.50;dy=half*.575+.065
    for offset in [-dy,0,dy]:
        for _,tree in NS['ai_trees']:
            hit,*_=tree.ray_cast(Vector((7,p.y+offset,p.z)),Vector((-1,0,0)),3.8)
            if hit and hit.x>=p.x-.44 and hit.x<6.1:p.x=max(p.x,hit.x+.45)
    return p

def map_vertex(v):
    t=max(0,min(1,-v.z/5.156512));p=center(t)
    if v.z>=-.025 and v.x<=1:
        u=max(0,min(1,(v.x+1)/2));start=Vector((3.98,1.76,9.89));p=start.lerp(center(0),u);p.z=9.89
        width=.13+.34*u**2
    else:width=.475*(.98+.035*math.sin(math.pi*t))
    normaloffset=(v.x-1.29449)*.24 if v.z<-.025 else 0
    p+=NS['ai_cross']*v.y*width+NS['ai_normal']*normaloffset
    if t>.96:
        for name,tree in NS['ai_trees']:
            if 'rock' not in name.lower():continue
            hit,*_=tree.ray_cast(Vector((p.x,p.y,3.65)),Vector((0,0,-1)),.8)
            if hit:p.z=max(p.z,hit.z+.075)
    return p

def build_asset_geometry():
    mats=[material('AI | Geometry silhouette test',shape=True),material('AI | Asset animated turquoise body'),material('AI | Asset aerated ridge details',ridge=True)]
    for source in NS['ai_imported']:
        if source.name.endswith('_b') or source.name=='falls_break_bottom_a':continue
        ob=source.copy();ob.data=source.data.copy();ob.name='AI adapted '+source.name;ob.matrix_world=Matrix.Identity(4);NS['ai_collection'].objects.link(ob)
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
        bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=6,use_grid_fill=True);bm.to_mesh(ob.data);bm.free()
        for v in ob.data.vertices:v.co=map_vertex(source.matrix_world@v.co)
        for p in ob.data.polygons:p.use_smooth=True;p.material_index=0
        ob.data.materials.clear();ob.data.materials.append(mats[0]);ob['asset_source_object']=source.name;ob['asset_license']='CC0'
    NS['ai_body_mat']=mats[1];NS['ai_detail_mat']=mats[2]
    variant('after');print('ADAPTED_ASSET_GEOMETRY',[(o.name,len(o.data.vertices)) for o in NS['ai_collection'].objects])

def apply_asset_materials():
    for ob in NS['ai_collection'].objects:
        if not ob.get('asset_source_object'):continue
        ob.data.materials[0]=NS['ai_body_mat'] if ob['asset_source_object']=='falls_layer_0' else NS['ai_detail_mat']
    print('DOWNLOADED_TEXTURE_CONNECTED_TO_RENDERED_PROTOTYPE')

def variant(which):
    for o in NS['ai_baseline']:o.hide_render=NS['ai_before_visibility'][o.name] if which=='before' else True
    for o in NS['ai_collection'].objects:o.hide_render=which!='after' or bool(o.get('AI disabled'))

def collisions():
    s=NS['ai_scene'];s.frame_set(75);dg=bpy.context.evaluated_depsgraph_get();out=[]
    for ob in NS['ai_collection'].objects:
        if ob.hide_render or ob.type!='MESH':continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
        for name,other in NS['ai_trees']:
            hits=tree.overlap(other)
            if hits:out.append((ob.name,name,len(hits)))
    print('ASSET_COLLISIONS',out);return out

def verify():
    changed=[n for n,h in NS['ai_protected'].items() if signature(bpy.data.objects[n])!=h];print('PROTECTED_CHANGES',changed);return changed

def render(which,filename,camera=None):
    s=NS['ai_scene'];bpy.context.window.scene=s;variant(which);s.frame_set(75);s.camera=camera or NS['ai_camera']
    s.render.image_settings.media_type='IMAGE';enum(s.render.image_settings,'file_format','PNG');s.render.filepath=ROOT+'/renders/'+filename;bpy.ops.render.render(write_still=True,scene=s.name)
    variant('after');s.camera=NS['ai_camera']

NS['ai_api']={'init':init,'background':background,'build_geometry':build_asset_geometry,'apply_materials':apply_asset_materials,'variant':variant,'collision':collisions,'verify':verify,'render':render}
