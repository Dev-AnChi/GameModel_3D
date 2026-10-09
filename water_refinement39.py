# -*- coding: utf-8 -*-
"""Waterfall_03 refinement, live Blender MCP only. Preserve the Pass A file."""
import bpy, math, json, hashlib, os, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT='C:/Game/GameModel_3D';NS=bpy.app.driver_namespace

def enum(o,p,value):
    values=[i.identifier for i in o.bl_rna.properties[p].enum_items]
    if values and value not in values:raise ValueError((p,value,values))
    setattr(o,p,value)

def signature(o):
    return hashlib.sha256(repr([o.name,o.type,[list(r) for r in o.matrix_world],
        [tuple(v.co) for v in o.data.vertices] if o.type=='MESH' else getattr(o.data,'name',None),
        [m.name if m else None for m in getattr(o.data,'materials',[])]]).encode('utf-8')).hexdigest()

def init():
    s=bpy.data.scenes['Scene'];bpy.context.window.scene=s;s.frame_set(75)
    NS['r39_protected']={o.name:signature(o) for o in s.objects}
    NS['r39_old']=list(bpy.data.collections['W39 | Pass A Waterfall Prototype'].objects)
    NS['r39_original']=[bpy.data.objects[n] for n in ['Waterfall_03','Organic cascade foam 2','Organic impact foam 2']]
    NS['r39_camera']=s.camera
    c=bpy.data.collections.new('R39 | Waterfall_03 Refined');s.collection.children.link(c);NS['r39_collection']=c
    # The source contains 65x9 vertices per lane, plus a separate spill-lip patch.
    src=bpy.data.objects['Waterfall_03']
    paths=[[src.matrix_world@src.data.vertices[lane*585+r*9+4].co for r in range(65)] for lane in range(3)]
    assert all(all(path[i].z>path[i+1].z for i in range(64)) for path in paths)
    NS['r39_source_paths']=paths
    print('SOURCE_ANCHORS',[(tuple(p[0]),tuple(p[-1])) for p in paths])
    trees=[];dg=bpy.context.evaluated_depsgraph_get()
    for o in s.objects:
        if o.type not in {'MESH','CURVE'} or o.hide_render or o.name.startswith(('W39','R39')):continue
        if any(x in o.name.lower() for x in ['water','cascade','foam','sea','ocean','pond','ripple','stream']):continue
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]
        if max(v.x for v in bb)<3.2 or min(v.x for v in bb)>6.4 or max(v.y for v in bb)<-.5 or min(v.y for v in bb)>2.6 or max(v.z for v in bb)<3.3 or min(v.z for v in bb)>10.1:continue
        ev=o.evaluated_get(dg);me=ev.to_mesh()
        if me and me.polygons:
            trees.append((o.name,BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])))
        ev.to_mesh_clear()
    NS['r39_static']=trees
    print('LOCAL_OBSTACLES',len(trees))

def texture_material(name,cycles,phase,aeration,clear=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;enum(m,'surface_render_method','DITHERED')
    n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    def node(t,x,y):a=n.new(t);a.location=(x,y);return a
    uv=node('ShaderNodeTexCoord',-1100,0)
    sc=node('ShaderNodeVectorMath',-920,0);enum(sc,'operation','MULTIPLY');sc.inputs[1].default_value=(1.35,3.6,1);l.new(uv.outputs['UV'],sc.inputs[0])
    add=node('ShaderNodeVectorMath',-740,0);enum(add,'operation','ADD');add.inputs[1].default_value=(phase*.31,0,0);l.new(sc.outputs[0],add.inputs[0]);add.inputs[1].driver_add('default_value',1).driver.expression=f'(frame-1)*{cycles}/300.0+{phase}'
    h=node('ShaderNodeTexImage',-560,220);h.image=bpy.data.images['height.png'];l.new(add.outputs[0],h.inputs['Vector']);enum(h,'extension','REPEAT')
    normal=node('ShaderNodeTexImage',-550,-250);normal.image=bpy.data.images['normal.png'];l.new(add.outputs[0],normal.inputs['Vector']);enum(normal,'extension','REPEAT')
    # A periodic carrier adds broad moving density packets without a photograph seam.
    sep=node('ShaderNodeSeparateXYZ',-570,500);l.new(add.outputs[0],sep.inputs[0])
    mul=node('ShaderNodeMath',-370,500);enum(mul,'operation','MULTIPLY');mul.inputs[1].default_value=math.tau;l.new(sep.outputs['Y'],mul.inputs[0])
    sine=node('ShaderNodeMath',-200,500);enum(sine,'operation','SINE');l.new(mul.outputs[0],sine.inputs[0])
    density=node('ShaderNodeMapRange',-20,470);density.inputs['From Min'].default_value=-1;density.inputs['From Max'].default_value=1;density.inputs['To Min'].default_value=.22;density.inputs['To Max'].default_value=.92;l.new(sine.outputs[0],density.inputs['Value'])
    nm=node('ShaderNodeNormalMap',-180,-210);nm.inputs['Strength'].default_value=.17 if not clear else .32;l.new(normal.outputs['Color'],nm.inputs['Color'])
    ramp=node('ShaderNodeValToRGB',160,430);ramp.color_ramp.elements[0].color=(.20,.42,.44,1) if clear else (.37,.64,.65,1);ramp.color_ramp.elements[1].color=(.82,.93,.94,1);l.new(density.outputs[0],ramp.inputs[0])
    bs=node('ShaderNodeBsdfPrincipled',420,190);bs.inputs['IOR'].default_value=1.333;bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.20 if not clear else .11;bs.inputs['Transmission Weight'].default_value=.10 if not clear else .35
    l.new(ramp.outputs[0],bs.inputs['Base Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
    opaque=node('ShaderNodeBsdfPrincipled',420,-110);opaque.inputs['Base Color'].default_value=(.78,.9,.91,1);opaque.inputs['Roughness'].default_value=.34;opaque.inputs['IOR'].default_value=1.333;l.new(nm.outputs[0],opaque.inputs['Normal'])
    mix=node('ShaderNodeMixShader',710,160);l.new(density.outputs[0],mix.inputs[0]);l.new(bs.outputs[0],mix.inputs[1]);l.new(opaque.outputs[0],mix.inputs[2])
    out=node('ShaderNodeOutputMaterial',970,140)
    if clear:
        tr=node('ShaderNodeBsdfTransparent',680,-200);al=node('ShaderNodeMapRange',430,-390);al.inputs['From Min'].default_value=0;al.inputs['From Max'].default_value=1;al.inputs['To Min'].default_value=.32;al.inputs['To Max'].default_value=.86;l.new(density.outputs[0],al.inputs['Value'])
        am=node('ShaderNodeMixShader',870,150);l.new(al.outputs[0],am.inputs[0]);l.new(tr.outputs[0],am.inputs[1]);l.new(mix.outputs[0],am.inputs[2]);l.new(am.outputs[0],out.inputs[0])
    else:l.new(mix.outputs[0],out.inputs[0])
    # Strong body is opaque through its depth; opacity is not a single low alpha plane.
    m['R39 role']='transparent edge' if clear else 'continuous volumetric aerated body'
    return m

def safe_x(p,half_width,half_depth):
    target=p.x
    for dy in [-half_depth,0,half_depth]:
        for name,t in NS['r39_static']:
            hit,n,idx,d=t.ray_cast(Vector((7,p.y+dy,p.z)),Vector((-1,0,0)),3.8)
            if hit and hit.x>=p.x-half_width and hit.x<6.1:target=max(target,hit.x+half_width+.045)
    return target

def volume(name,path,width,depth,phase,mat,clear=False):
    vs=[];uvs=[];faces=[];centers=[];sections=16
    # Smooth the clearance envelope before making rings, preventing rock-driven kinks.
    candidates=[];sizes=[]
    for i,p in enumerate(path):
        t=i/(len(path)-1);w=width*(.90+.12*math.sin(t*13+phase)+.09*math.sin(t*31+phase));d=depth*(.8+.2*math.sin(t*17+phase))
        candidates.append(safe_x(p,w/2,d/2));sizes.append((w,d))
    for _ in range(5):
        candidates=[max(candidates[i],sum(candidates[max(0,i-2):min(len(path),i+3)])/len(candidates[max(0,i-2):min(len(path),i+3)])) for i in range(len(path))]
    for i,p in enumerate(path):
        t=i/(len(path)-1);w,d=sizes[i];p=p.copy();p.x=candidates[i];centers.append(p)
        for j in range(sections):
            a=math.tau*j/sections
            # Lobed, flattened water cross-section; no duplicated front/back alpha planes.
            rough=1+.10*math.sin(3*a+t*27+phase)+.055*math.sin(7*a-t*41)
            v=p+Vector((math.cos(a)*w*.5*rough,math.sin(a)*d*.5*rough,0))
            vs.append(v);uvs.append((j/sections,1-t))
        if i:
            for j in range(sections):a=(i-1)*sections+j;b=(i-1)*sections+(j+1)%sections;faces.append((a,b,b+sections,a+sections))
    faces.extend([tuple(reversed(range(sections))),tuple((len(path)-1)*sections+j for j in range(sections))])
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();uv=me.uv_layers.new(name='FlowUV')
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
    o=bpy.data.objects.new(name,me);NS['r39_collection'].objects.link(o);me.materials.append(mat)
    o['R39 role']='edge stream' if clear else 'main body';NS.setdefault('r39_paths',{})[name]=centers
    return o

def build_body():
    paths=NS['r39_source_paths'];base=paths[0];body=[]
    for i,p in enumerate(base):
        t=i/64;p=p.copy();p.y-=.44*math.sin(math.pi*t)**.8
        p.x+=.08*math.sin(math.pi*t);body.append(p)
    mats=[texture_material('R39 | Main water mass',23,0,.65),texture_material('R39 | Aerated secondary',29,.37,.8),texture_material('R39 | Clear edge',37,.71,.2,True)]
    volume('R39 main continuous mass',body,.86,.22,.2,mats[0])
    secondary=[p+Vector((.32*math.sin(math.pi*i/64),-.05,0)) for i,p in enumerate(body)]
    volume('R39 secondary aerated mass',secondary,.39,.15,2.1,mats[1])
    for k,(start,end) in enumerate([(8,39),(22,61),(4,27),(34,64)]):
        path=[]
        for i in range(start,end+1):
            t=(i-start)/(end-start);p=body[i].copy();p.x+=(1 if k%2 else -1)*(.46+.10*math.sin(t*math.pi));p.y-=.05+.08*math.sin(t*math.pi);path.append(p)
        # Width collapses near endpoints through ring geometry, not large transparent cards.
        ob=volume('R39 short separated stream '+str(k),path,.065+.017*k,.038,k,mats[2],True)
        rings=len(path);me=ob.data
        for i in range(rings):
            t=i/(rings-1);fac=.08+.92*math.sin(math.pi*t)**.6
            center=NS['r39_paths'][ob.name][i]
            for v in list(me.vertices)[i*16:(i+1)*16]:v.co=center+(v.co-center)*fac
    variant('refined');print('BODY_BUILT',[(o.name,len(o.data.vertices)) for o in NS['r39_collection'].objects])

def variant(which):
    for o in NS['r39_original']:o.hide_render=which!='original'
    for o in NS['r39_old']:o.hide_render=which!='pass_a';o.hide_set(which!='pass_a')
    for o in NS['r39_collection'].objects:o.hide_render=which!='refined' or bool(o.get('R39 disabled'))

def render(which,filename):
    s=bpy.data.scenes['Scene'];bpy.context.window.scene=s;variant(which);s.camera=NS['r39_camera'];s.frame_set(75)
    s.render.image_settings.media_type='IMAGE';enum(s.render.image_settings,'file_format','PNG');s.render.filepath=ROOT+'/renders/'+filename
    bpy.ops.render.render(write_still=True,scene=s.name);variant('refined')

def collision_check():
    out=[]
    for o in NS['r39_collection'].objects:
        if o.get('R39 role') not in {'main body','edge stream'}:continue
        t=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
        for name,tree in NS['r39_static']:
            hits=t.overlap(tree)
            if hits:out.append((o.name,name,len(hits)))
    print('COLLISION',out);return out

def verify():
    changed=[n for n,v in NS['r39_protected'].items() if signature(bpy.data.objects[n])!=v]
    print('SOURCE_STRUCTURAL_CHANGES',changed)

NS['r39_api']={'init':init,'build_body':build_body,'render':render,'variant':variant,'collision':collision_check,'verify':verify}

def refine_surface():
    for name in ['R39 | Main water mass','R39 | Aerated secondary','R39 | Clear edge']:
        m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links
        add=next(a for a in n if a.bl_idname=='ShaderNodeVectorMath' and a.operation=='ADD')
        def new(t):return n.new(t)
        # Integer scroll cycles preserve frame 1/301, with seam-free procedural density.
        noise=new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=4.8;noise.inputs['Detail'].default_value=3.0;noise.inputs['Roughness'].default_value=.7
        stretch=new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(3.2,.32,1);l.new(add.outputs[0],stretch.inputs[0]);l.new(stretch.outputs[0],noise.inputs['Vector'])
        # Periodic texture coordinate via sine/cosine cancels spatial scroll seams.
        sep=new('ShaderNodeSeparateXYZ');l.new(add.outputs[0],sep.inputs[0])
        mul=new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=math.tau;l.new(sep.outputs['Y'],mul.inputs[0])
        si=new('ShaderNodeMath');si.operation='SINE';l.new(mul.outputs[0],si.inputs[0])
        co=new('ShaderNodeMath');co.operation='COSINE';l.new(mul.outputs[0],co.inputs[0])
        combine=new('ShaderNodeCombineXYZ');l.new(sep.outputs['X'],combine.inputs['X']);l.new(si.outputs[0],combine.inputs['Y']);l.new(co.outputs[0],combine.inputs['Z']);l.new(combine.outputs[0],stretch.inputs[0])
        density=next(a for a in n if a.bl_idname=='ShaderNodeMapRange')
        density.inputs['From Min'].default_value=.30;density.inputs['From Max'].default_value=.70;density.inputs['To Min'].default_value=.05;density.inputs['To Max'].default_value=.95;density.clamp=True;l.new(noise.outputs['Fac'],density.inputs['Value'])
        ramp=next(a for a in n if a.bl_idname=='ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.065,.17,.18,1);ramp.color_ramp.elements[1].color=(.88,.96,.96,1)
        bs=[a for a in n if a.bl_idname=='ShaderNodeBsdfPrincipled'];bs[0].inputs['Transmission Weight'].default_value=.65;bs[0].inputs['Roughness'].default_value=.12;bs[1].inputs['Roughness'].default_value=.24
        bump=new('ShaderNodeBump');bump.inputs['Strength'].default_value=.48;bump.inputs['Distance'].default_value=.045;l.new(noise.outputs['Fac'],bump.inputs['Height'])
        normal=next(a for a in n if a.bl_idname=='ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65;l.new(normal.outputs[0],bump.inputs['Normal'])
        for a in bs:l.new(bump.outputs[0],a.inputs['Normal'])
    print('SURFACE_REFINED')

NS['r39_api']['refine_surface']=refine_surface

def flowing_detail():
    for name in ['R39 | Main water mass','R39 | Aerated secondary','R39 | Clear edge']:
        m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links
        add=next(a for a in n if a.bl_idname=='ShaderNodeVectorMath' and a.operation=='ADD')
        def new(t):return n.new(t)
        def op(kind,a,b=None):
            q=new('ShaderNodeMath');q.operation=kind
            l.new(a,q.inputs[0]) if hasattr(a,'node') else setattr(q.inputs[0],'default_value',a)
            if b is not None:
                l.new(b,q.inputs[1]) if hasattr(b,'node') else setattr(q.inputs[1],'default_value',b)
            return q.outputs[0]
        sc=next(a for a in n if a.bl_idname=='ShaderNodeVectorMath' and a.operation=='MULTIPLY');sc.inputs[1].default_value=(1.0,2.2,1)
        photo=new('ShaderNodeTexImage');photo.image=bpy.data.images['oga_waterfall_1.png'];photo.extension='REPEAT';l.new(add.outputs[0],photo.inputs[0])
        bw=new('ShaderNodeRGBToBW');l.new(photo.outputs[0],bw.inputs[0])
        sep=new('ShaderNodeSeparateXYZ');l.new(add.outputs[0],sep.inputs[0])
        fy=op('FRACT',sep.outputs['Y']);window=op('POWER',op('SINE',op('MULTIPLY',fy,math.pi)),2)
        blend=new('ShaderNodeMixRGB');l.new(window,blend.inputs[0]);blend.inputs[1].default_value=(.62,.62,.62,1);l.new(bw.outputs[0],blend.inputs[2])
        density=next(a for a in n if a.bl_idname=='ShaderNodeMapRange');density.inputs['From Min'].default_value=.17;density.inputs['From Max'].default_value=.78;density.inputs['To Min'].default_value=.10;density.inputs['To Max'].default_value=1;l.new(blend.outputs[0],density.inputs['Value'])
        bump=next(a for a in n if a.bl_idname=='ShaderNodeBump');bump.inputs['Strength'].default_value=.20;bump.inputs['Distance'].default_value=.015;l.new(blend.outputs[0],bump.inputs['Height'])
        normal=next(a for a in n if a.bl_idname=='ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.23
        ramp=next(a for a in n if a.bl_idname=='ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.12,.28,.30,1);ramp.color_ramp.elements[1].color=(.95,.99,1,1)
        bs=[a for a in n if a.bl_idname=='ShaderNodeBsdfPrincipled'];bs[1].inputs['Base Color'].default_value=(.95,.99,1,1);bs[1].inputs['Emission Color'].default_value=(.65,.77,.8,1);bs[1].inputs['Emission Strength'].default_value=.26
    for ob in NS['r39_collection'].objects:
        if ob.get('R39 role')!='main body':continue
        path=NS['r39_paths'][ob.name];ob.shape_key_add(name='Basis')
        for k in range(2):
            key=ob.shape_key_add(name='Flow pulse '+str(k))
            for i,p in enumerate(path):
                t=i/(len(path)-1);strength=math.sin(math.pi*t)**.5
                for j in range(16):
                    idx=i*16+j;v=key.data[idx];a=math.tau*j/16
                    shrink=.74+.23*math.sin(t*25+.7)+.09*math.sin(t*67)
                    # Fluted cross-section breaks smooth cloth highlights.
                    v.co.x=p.x+(v.co.x-p.x)*shrink+.025*strength*math.sin(t*45+k*math.pi/2)
                    v.co.y+=.025*strength*math.sin(5*a+t*53+k*math.pi/2)
            key.value=.5;key.driver_add('value').driver.expression=f'.5+.5*sin(2*pi*(frame-1)*{7+k*4}/300+{k*math.pi/2})'
    print('FLOWING_DETAIL_READY')

NS['r39_api']['flowing_detail']=flowing_detail

def final_body_masks():
    for name in ['R39 | Main water mass','R39 | Aerated secondary','R39 | Clear edge']:
        m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links
        add=next(a for a in n if a.bl_idname=='ShaderNodeVectorMath' and a.operation=='ADD')
        blend=next(a for a in n if a.bl_idname=='ShaderNodeMixRGB')
        offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.37,.5,0);l.new(add.outputs[0],offset.inputs[0])
        image=n.new('ShaderNodeTexImage');image.image=bpy.data.images['oga_waterfall_1.png'];image.extension='REPEAT';l.new(offset.outputs[0],image.inputs[0]);l.new(image.outputs[0],blend.inputs[1])
        density=next(a for a in n if a.bl_idname=='ShaderNodeMapRange');density.inputs['From Min'].default_value=.35;density.inputs['From Max'].default_value=.88
        out=next(a for a in n if a.bl_idname=='ShaderNodeOutputMaterial')
        if 'Clear edge' in name:
            density.inputs['To Max'].default_value=.40
            for bs in [a for a in n if a.bl_idname=='ShaderNodeBsdfPrincipled']:bs.inputs['Emission Strength'].default_value=0;bs.inputs['Transmission Weight'].default_value=.80
        else:
            prior=out.inputs[0].links[0].from_socket
            opacity=n.new('ShaderNodeMapRange');opacity.inputs['To Min'].default_value=.52;opacity.inputs['To Max'].default_value=1;l.new(density.outputs[0],opacity.inputs['Value'])
            transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(opacity.outputs[0],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(prior,mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
    print('DENSITY_MASKS_FINAL')

def mesh_object(name,verts,faces,mat,uvs=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat)
    uv=me.uv_layers.new(name='FlowUV')
    for poly in me.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            i=me.loops[li].vertex_index;uv.data[li].uv=uvs[i] if uvs else (verts[i][0],verts[i][1])
    ob=bpy.data.objects.new(name,me);NS['r39_collection'].objects.link(ob);return ob

def build_contact():
    rng=random.Random(3909);bodymat=bpy.data.materials['R39 | Main water mass'];clear=bpy.data.materials['R39 | Clear edge']
    foam=bodymat.copy();foam.name='R39 | Contact foam moving microbubbles'
    for fc in foam.node_tree.animation_data.drivers:fc.driver.expression='(frame-1)*9/300.0+.24'
    centers=NS['r39_paths']['R39 main continuous mass'];top=centers[0];base=centers[-1]
    # Thin water spill surface conforms to rock rather than a spherical cap.
    vs=[];uv=[];faces=[]
    for i in range(17):
        t=i/16;x=3.98+(top.x-3.98)*t;y=2.05+(top.y-2.05)*t
        for j in range(13):
            a=j/12-.5;px=x+a*.72;py=y
            z=9.86+.028*math.sin(j*1.6+i*.7)
            for _,tree in NS['r39_static']:
                hit,*_=tree.ray_cast(Vector((px,py,10.12)),Vector((0,0,-1)),.6)
                if hit:z=max(z,hit.z+.025)
            vs.append((px,py,z));uv.append((j/12,1-t*.25))
            if i and j:q=i*13+j;faces.append((q-14,q-13,q,q-1))
    mesh_object('R39 rock-lip overflowing water',vs,faces,bodymat,uv)
    # Irregular shallow impact foam surface, no white sphere cluster.
    vs=[tuple(base+Vector((0,0,.035)))];uv=[(.5,.5)];faces=[]
    for ring in range(1,7):
        r=ring/6
        for j in range(64):
            a=math.tau*j/64;rough=1+.10*math.sin(5*a)+.08*math.sin(9*a+1)
            v=base+Vector((.57*r*rough*math.cos(a),.38*r*rough*math.sin(a),.04+.04*math.sin(a*7+r*19)*r))
            vs.append(tuple(v));uv.append((.5+.5*r*math.cos(a),.5+.5*r*math.sin(a)))
            if ring==1:faces.append((0,1+j,1+(j+1)%64))
            else:a0=1+(ring-2)*64+j;b0=1+(ring-2)*64+(j+1)%64;faces.append((a0,b0,b0+64,a0+64))
    impact=mesh_object('R39 turbulent impact foam patch',vs,faces,foam,uv)
    impact.location=(0,0,0);impact.driver_add('location',2).driver.expression='.012*sin(2*pi*(frame-1)*17/300)'
    # Small contact foam streaks only where water bends over the lip.
    for k in range(5):
        start=top+Vector(((k-2)*.14,-.12,0));verts=[];uvs=[];fs=[]
        for j in range(9):
            t=j/8;w=.014+.013*math.sin(math.pi*t)
            p=start+Vector((.035*math.sin(t*5+k),-.02,-.32*t))
            for side in [-1,1]:verts.append(tuple(p+Vector((side*w,0,0))));uvs.append(((side+1)/2,1-t))
            if j:idx=j*2;fs.append((idx-2,idx-1,idx+1,idx))
        mesh_object('R39 lip foam streak '+str(k),verts,fs,foam,uvs)
    # Upward splash fingers with independent ballistic phases, small tapered tubes.
    for k in range(16):
        angle=rng.uniform(0,math.tau);period=rng.choice([50,60,75,100]);phase=rng.random();height=rng.uniform(.13,.48);rad=rng.uniform(.14,.50)
        vs=[];uv=[];faces=[]
        for j in range(13):
            t=j/12;p=Vector((math.cos(angle)*rad*t,math.sin(angle)*rad*t,4*height*t*(1-t)))
            for q in range(6):
                a=math.tau*q/6;w=.010*(1-t)+.002
                vs.append(tuple(p+Vector((w*math.cos(a),w*math.sin(a),0))));uv.append((q/6,t))
                if j:idx=j*6+q;b=j*6+(q+1)%6;faces.append((idx-6,b-6,b,idx))
        ob=mesh_object('R39 upward splash finger '+str(k),vs,faces,foam,uv);ob.location=base+Vector((0,0,.06))
        for axis in range(3):ob.driver_add('scale',axis).driver.expression=f'.12+.88*sin(pi*((((frame-1)/{period}+{phase})%1)))**2'
    for k in range(52):
        a=rng.uniform(0,math.tau);radius=rng.uniform(.15,.65);h=rng.uniform(.14,.60);period=rng.choice([30,50,60,75,100]);phase=rng.random();size=rng.uniform(.008,.020)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=size,location=base)
        ob=bpy.context.object;ob.name='R39 detached splash droplet '+str(k)
        for c in list(ob.users_collection):c.objects.unlink(ob)
        NS['r39_collection'].objects.link(ob);ob.data.materials.append(clear if k%3 else foam);ob.scale=(.7,.7,1.7)
        t=f'(((frame-1)/{period}+{phase})%1)'
        for axis,v in [(0,math.cos(a)*radius),(1,math.sin(a)*radius)]:ob.driver_add('location',axis).driver.expression=f'{base[axis]}+{v}*{t}'
        ob.driver_add('location',2).driver.expression=f'{base.z+.06}+4*{h}*{t}*(1-{t})'
        for axis,f in enumerate([.7,.7,1.7]):ob.driver_add('scale',axis).driver.expression=f'{f}*sin(pi*{t})**2'
    # Sparse expanding, broken ripples at the impact location.
    for k in range(5):
        vs=[];uv=[];fs=[]
        for j in range(81):
            a=math.tau*j/100+k*.41
            for side in [-1,1]:r=.32+side*.006;vs.append((r*math.cos(a),r*.66*math.sin(a),.004*math.sin(a*11)));uv.append(((side+1)/2,j/80))
            if j:idx=j*2;fs.append((idx-2,idx-1,idx+1,idx))
        ripplemat=clear.copy();ripplemat.name='R39 | Ripple fade '+str(k)
        n=ripplemat.node_tree.nodes;l=ripplemat.node_tree.links;out=next(q for q in n if q.bl_idname=='ShaderNodeOutputMaterial');prior=out.inputs[0].links[0].from_socket
        info=n.new('ShaderNodeObjectInfo');tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(info.outputs['Alpha'],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(prior,mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
        ob=mesh_object('R39 expanding broken ripple '+str(k),vs,fs,ripplemat,uv);ob.location=base+Vector((0,0,.025));period=[60,75,100,50,60][k];phase=k*.197
        for axis in [0,1]:ob.driver_add('scale',axis).driver.expression=f'.15+2.3*(((frame-1)/{period}+{phase})%1)'
        ob.driver_add('scale',2).driver.expression=f'sin(pi*(((frame-1)/{period}+{phase})%1))**2'
        ob.driver_add('color',3).driver.expression=f'sin(pi*(((frame-1)/{period}+{phase})%1))**2'
    print('CONTACT_READY',len(NS['r39_collection'].objects))

NS['r39_api'].update(final_masks=final_body_masks,contact=build_contact)

def break_sheet_silhouette():
    for ob in NS['r39_collection'].objects:
        if ob.get('R39 role') not in {'main body','edge stream'}:continue
        path=NS['r39_paths'][ob.name]
        blocks=list(ob.data.shape_keys.key_blocks) if ob.data.shape_keys else []
        datasets=[ob.data.vertices]+[key.data for key in blocks]
        for data in datasets:
            for i,p in enumerate(path):
                t=i/(len(path)-1)
                for j in range(16):
                    v=data[i*16+j];a=math.tau*j/16
                    if ob.get('R39 role')=='main body':
                        factor=(.70 if 'main continuous' in ob.name else .85)*(.82+.16*math.sin(i*.83)+.08*math.sin(i*1.91))
                        factor*=.55+.45*min(1,i/4)
                        v.co.x=p.x+(v.co.x-p.x)*factor
                        v.co.y=p.y+(v.co.y-p.y)*1.65+.022*math.sin(i*1.7+j*.9)
                        if 'secondary' in ob.name:v.co.x+=.13*math.sin(math.pi*t)
                    else:v.co.x+=.045*math.sin(i*.37)+.025*math.sin(i*.91);v.co.y+=.035*math.sin(i*.53)
    print('SILHOUETTE_BROKEN')

def evaluated_collisions():
    scene=bpy.data.scenes['Scene'];out=[]
    for frame in [1,26,51,76,101,126,151,176,201,226,251,276,301]:
        scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get()
        for ob in NS['r39_collection'].objects:
            if ob.hide_render:continue
            ev=ob.evaluated_get(dg);me=ev.to_mesh()
            tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
            for name,other in NS['r39_static']:
                hit=tree.overlap(other)
                if hit:out.append((frame,ob.name,name,len(hit)))
    scene.frame_set(75);NS['r39_collision_samples']=out;print('EVALUATED_COLLISIONS',out[:100]);return out

NS['r39_api'].update(silhouette=break_sheet_silhouette,evaluated_collisions=evaluated_collisions)

def contact_clearance():
    base=NS['r39_paths']['R39 main continuous mass'][-1]
    for ob in NS['r39_collection'].objects:
        if ob.name=='R39 rock-lip overflowing water':
            for v in ob.data.vertices:
                v.co.z+=.035;v.co.x=safe_x(v.co,0,.01)+.035
        if ob.name=='R39 turbulent impact foam patch':
            me=ob.data;verts=[tuple(base+Vector((.065,0,.06)))];faces=[];uvs=[(0,.5)]
            for ring in range(1,7):
                r=ring/6
                for j in range(65):
                    a=-math.pi/2+math.pi*j/64;rough=1+.09*math.sin(a*7+r*3)
                    verts.append(tuple(base+Vector((.065+.56*r*rough*math.cos(a),.34*r*rough*math.sin(a),.06+.018*r*math.sin(a*7+r*19)))))
                    uvs.append((r*math.cos(a),.5+.5*r*math.sin(a)))
                    if j:
                        q=1+(ring-1)*65+j
                        if ring==1:faces.append((0,q-1,q))
                        else:faces.append((q-66,q-65,q,q-1))
            fresh=mesh_object('R39 temporary impact rebuild',verts,faces,me.materials[0],uvs);ob.data=fresh.data;bpy.data.objects.remove(fresh,do_unlink=True)
        if ob.name.startswith('R39 expanding broken ripple'):
            for j in range(81):
                angle=-math.pi/2+math.pi*j/80
                for q,side in enumerate([-1,1]):r=.32+side*.006;ob.data.vertices[j*2+q].co=(r*math.cos(angle),r*.66*math.sin(angle),.004*math.sin(angle*11))
            ob.location.x=base.x+.085
        if ob.name.startswith('R39 upward splash finger'):
            for v in ob.data.vertices:v.co.x=abs(v.co.x)+.035
    print('CONTACT_CLEARANCE_FIXED')

NS['r39_api']['contact_clearance']=contact_clearance

def setup_preview():
    source=bpy.data.scenes['W39 | Prototype Animation Review'];scene=source.copy();scene.name='R39 | Refined Waterfall Animation Review'
    if NS['r39_collection'].name not in scene.collection.children:scene.collection.children.link(NS['r39_collection'])
    scene.frame_start=1;scene.frame_end=300;scene.render.fps=30;scene.render.fps_base=1;scene.camera=NS['r39_camera']
    scene.render.resolution_x=464;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=48
    NS['r39_preview']=scene
    cameras={}
    for label,target in [('top',(4.65,1.72,9.57)),('middle',(4.85,1.16,6.6)),('base',(5.22,1.1,3.65))]:
        data=bpy.data.cameras.new('R39 close-up '+label);ob=bpy.data.objects.new(data.name,data);bpy.data.scenes['Scene'].collection.objects.link(ob)
        target=Vector(target);ob.location=target+Vector((9.5,-13.5,2.4));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=2.15;cameras[label]=ob
    NS['r39_closeup_cameras']=cameras
    print('PREVIEW_READY',scene.name,len(scene.objects))

def compare_renders():
    render('original','waterfall_original_refine_compare.png');render('pass_a','waterfall_pass_a_refine_compare.png')
    scene=bpy.data.scenes['Scene'];variant('refined');scene.frame_set(75)
    for label,cam in NS['r39_closeup_cameras'].items():
        scene.camera=cam;scene.render.filepath=ROOT+'/renders/waterfall_refined_closeup_'+label+'.png';bpy.ops.render.render(write_still=True,scene=scene.name)
    scene.camera=NS['r39_camera'];scene.frame_set(75)
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Catmosphere_Water_Refined.blend')
    print('COMPARISONS_DONE')

def loop_check():
    scene=NS['r39_preview'];previous=bpy.context.window.scene;bpy.context.window.scene=scene;variant('refined')
    def snap(frame):
        scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();state={}
        for ob in NS['r39_collection'].objects:
            ev=ob.evaluated_get(dg);me=ev.to_mesh();state[ob.name]=[tuple(ev.matrix_world@v.co) for v in me.vertices];ev.to_mesh_clear()
        return state
    a=snap(1);b=snap(301);delta=max((Vector(v)-Vector(w)).length for name in a for v,w in zip(a[name],b[name]))
    scene.frame_set(1);scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.filepath=ROOT+'/renders/water_refined_loop_001.png';bpy.ops.render.render(write_still=True,scene=scene.name)
    scene.frame_set(301);scene.render.filepath=ROOT+'/renders/water_refined_loop_301.png';bpy.ops.render.render(write_still=True,scene=scene.name)
    NS['r39_loop_geometry_delta']=delta;scene.frame_set(75);bpy.context.window.scene=previous;print('LOOP_GEOMETRY_MAX_DELTA',delta)

def preview_render():
    scene=NS['r39_preview'];bpy.context.window.scene=scene;variant('refined');scene.frame_set(1)
    scene.render.image_settings.media_type='VIDEO';scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='HIGH';scene.render.ffmpeg.gopsize=30
    scene.render.filepath=ROOT+'/renders/waterfall_refined_animation_preview.mp4';bpy.ops.render.render(animation=True,scene=scene.name)
    bpy.context.window.scene=bpy.data.scenes['Scene'];bpy.data.scenes['Scene'].camera=NS['r39_camera'];bpy.data.scenes['Scene'].frame_set(75)
    verify();bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Catmosphere_Water_Refined.blend');print('REFINED_PREVIEW_FINISHED')

NS['r39_api'].update(setup_preview=setup_preview,compare=compare_renders,loop=loop_check,preview=preview_render)

def rounded_spill_connector():
    old=bpy.data.objects['R39 rock-lip overflowing water'];old.hide_render=True;old.hide_set(True);old['R39 disabled']=True
    centers=NS['r39_paths']['R39 main continuous mass'];p0=Vector((3.98,1.76,9.86));p1=Vector((4.65,1.76,9.9));p2=centers[0]+Vector((.02,0,.06));p3=centers[3]
    verts=[];uvs=[];faces=[]
    for i in range(33):
        t=i/32;p=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
        tangent=(3*(1-t)**2*(p1-p0)+6*(1-t)*t*(p2-p1)+3*t*t*(p3-p2)).normalized();cross=Vector((-tangent.z,0,tangent.x)).normalized()
        width=.04+.42*t**1.7;depth=.11+.19*t
        for j in range(16):
            a=math.tau*j/16;v=p+cross*math.cos(a)*width/2+Vector((0,math.sin(a)*depth/2,0));verts.append(tuple(v));uvs.append((j/16,1-t*.18))
            if i:q=i*16+j;b=i*16+(j+1)%16;faces.append((q-16,b-16,b,q))
    ob=mesh_object('R39 rounded overflowing spill connector',verts,faces,bpy.data.materials['R39 | Main water mass'],uvs)
    print('ROUNDED_SPILL_CONNECTED')

NS['r39_api']['spill_connector']=rounded_spill_connector

def bury_old_head_caps():
    for name in ['R39 main continuous mass','R39 secondary aerated mass']:
        ob=bpy.data.objects[name];path=NS['r39_paths'][name];target=NS['r39_paths']['R39 main continuous mass'][3]
        datasets=[ob.data.vertices]+[key.data for key in ob.data.shape_keys.key_blocks]
        for data in datasets:
            for i in range(3):
                for j in range(16):
                    v=data[i*16+j];delta=v.co-path[i];v.co=target+Vector((delta.x*.45,delta.y*.40,.08-i*.022))
    print('HEAD_CAPS_BURIED_INSIDE_SPILL')

NS['r39_api']['bury_caps']=bury_old_head_caps

def grounded_impact():
    rocks=[t for name,t in NS['r39_static'] if 'rock' in name.lower()]
    for ob in NS['r39_collection'].objects:
        if ob.get('R39 role')=='main body':
            datasets=[ob.data.vertices]+[key.data for key in ob.data.shape_keys.key_blocks]
            for data in datasets:
                for i in range(60,65):
                    for j in range(16):data[i*16+j].co.z-=.12*((i-60)/4)**2
        elif ob.name=='R39 turbulent impact foam patch':
            for v in ob.data.vertices:
                heights=[]
                for tree in rocks:
                    hit,*_=tree.ray_cast(Vector((v.co.x,v.co.y,3.6)),Vector((0,0,-1)),.8)
                    if hit:heights.append(hit.z)
                if heights:v.co.z=max(heights)+.045
            for fc in ob.animation_data.drivers:fc.driver.expression='.006*sin(2*pi*(frame-1)*17/300)'
        elif ob.name.startswith('R39 upward splash finger'):
            ob.location.z-=.19
            if int(ob.name.rsplit(' ',1)[-1])%3:
                ob['R39 disabled']=True;ob.hide_render=True
        elif ob.name.startswith('R39 detached splash droplet'):
            fc=next(f for f in ob.animation_data.drivers if f.data_path=='location' and f.array_index==2);fc.driver.expression=fc.driver.expression.replace('3.510000047683716','3.320000047683716')
        elif ob.name.startswith('R39 expanding broken ripple'):
            ob.location.x=5.35;ob.location.z=3.112
    print('IMPACT_GROUNDED')

NS['r39_api']['grounded_impact']=grounded_impact

def surface_contact_clamp():
    rocks=[t for name,t in NS['r39_static'] if 'rock' in name.lower()]
    for ob in NS['r39_collection'].objects:
        if ob.get('R39 role')=='main body':
            datasets=[ob.data.vertices]+[key.data for key in ob.data.shape_keys.key_blocks]
            for data in datasets:
                for v in list(data)[62*16:]:
                    for tree in rocks:
                        hit,*_=tree.ray_cast(Vector((v.co.x,v.co.y,3.6)),Vector((0,0,-1)),.8)
                        if hit:v.co.z=max(v.co.z,hit.z+.035)
        if ob.name.startswith('R39 upward splash finger'):ob.location.z+=.065
    print('ROCK_SURFACE_CONTACT_CLAMPED')

NS['r39_api']['surface_contact_clamp']=surface_contact_clamp

def continuous_head_and_impact():
    ob=bpy.data.objects['R39 rounded overflowing spill connector'];ob['R39 disabled']=True;ob.hide_render=True
    rocks=[t for name,t in NS['r39_static'] if 'rock' in name.lower()]
    source=NS['r39_paths']['R39 main continuous mass'];p0=Vector((3.98,1.76,9.86));p1=Vector((4.6,1.76,9.92));p2=Vector((4.95,1.66,9.65));p3=source[8]
    for name in ['R39 main continuous mass','R39 secondary aerated mass']:
        ob=bpy.data.objects[name];datasets=[ob.data.vertices]+[key.data for key in ob.data.shape_keys.key_blocks]
        for data in datasets:
            for i in range(9):
                t=i/8;p=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
                tangent=(3*(1-t)**2*(p1-p0)+6*(1-t)*t*(p2-p1)+3*t*t*(p3-p2)).normalized();cross=Vector((-tangent.z,0,tangent.x)).normalized()
                width=.035+.45*t**.8;depth=.11+.20*t
                if 'secondary' in name:width*=.6;depth*=.65;p.x+=.08*t
                for j in range(16):
                    a=math.tau*j/16;data[i*16+j].co=p+cross*math.cos(a)*width/2+Vector((0,math.sin(a)*depth/2,0))
            for i in [63,64]:
                for j in range(16):
                    v=data[i*16+j];hits=[]
                    for tree in rocks:
                        hit,*_=tree.ray_cast(Vector((v.co.x,v.co.y,3.6)),Vector((0,0,-1)),.8)
                        if hit:hits.append(hit.z)
                    if hits:
                        target=max(hits)+.06;v.co.z=target if i==64 else max(target,.5*(v.co.z+target))
    print('CONTINUOUS_HEAD_AND_IMPACT')

NS['r39_api']['continuous_head_and_impact']=continuous_head_and_impact
