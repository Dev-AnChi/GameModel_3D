# -*- coding: utf-8 -*-
"""Pass A only; run in live Blender through MCP. Sources are preserved."""
import bpy, math, json, hashlib, os, random
from mathutils import Vector
ROOT='C:/Game/GameModel_3D'
NS=bpy.app.driver_namespace

def signature(o):
    payload=[o.name,o.type,[list(r) for r in o.matrix_world],getattr(o.data,'name',None),[m.name if m else None for m in getattr(o.data,'materials',[])]]
    if o.type=='MESH': payload.append([tuple(v.co) for v in o.data.vertices])
    return hashlib.sha256(repr(payload).encode('utf-8')).hexdigest()

def build():
    s=bpy.data.scenes['Scene'];src=bpy.data.objects['Waterfall_03']
    NS['w39_protected']={o.name:signature(o) for o in s.objects}
    c=bpy.data.collections.new('W39 | Pass A Waterfall Prototype');s.collection.children.link(c)
    normal=bpy.data.images.load(ROOT+'/textures/water/wave-normal-map/water-wave-normal-map-1k/normal.png',check_existing=True)
    height=bpy.data.images.load(ROOT+'/textures/water/wave-normal-map/water-wave-normal-map-1k/height.png',check_existing=True)
    for im in [normal,height]: im.colorspace_settings.name='Non-Color';im.pack();print('VALIDATED',im.name,tuple(im.size))
    mats=[]
    for lane,cycles in enumerate([3,5,7]):
        m=bpy.data.materials.new('W39 | layered flowing water '+str(lane));m.use_nodes=True
        m.surface_render_method='DITHERED';n=m.node_tree.nodes;n.clear();l=m.node_tree.links
        def node(t,x,y):
            a=n.new(t);a.location=(x,y);return a
        uv=node('ShaderNodeTexCoord',-900,0)
        scale=node('ShaderNodeVectorMath',-720,0);scale.operation='MULTIPLY';scale.inputs[1].default_value=(2.7,0.65,1);l.new(uv.outputs['UV'],scale.inputs[0])
        add=node('ShaderNodeVectorMath',-540,0);add.operation='ADD';add.label='Seamless downward flow: integer tiles / 300 frames';add.inputs[1].default_value=(lane*.217,0,0)
        add.inputs[1].driver_add('default_value',1).driver.expression=f'(frame-1)*{cycles}/300.0';l.new(scale.outputs[0],add.inputs[0])
        tex=node('ShaderNodeTexImage',-340,-150);tex.image=normal;tex.extension='REPEAT';l.new(add.outputs[0],tex.inputs['Vector'])
        norm=node('ShaderNodeNormalMap',-90,-160);norm.inputs['Strength'].default_value=.28;l.new(tex.outputs['Color'],norm.inputs['Color'])
        h=node('ShaderNodeTexImage',-340,180);h.image=height;h.extension='REPEAT';l.new(add.outputs[0],h.inputs['Vector'])
        ramp=node('ShaderNodeValToRGB',-80,190);ramp.color_ramp.elements[0].position=.28;ramp.color_ramp.elements[0].color=(.24,.49,.51,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(.88,.97,1,1);l.new(h.outputs['Color'],ramp.inputs[0])
        bs=node('ShaderNodeBsdfPrincipled',170,130);bs.inputs['Roughness'].default_value=.16;bs.inputs['IOR'].default_value=1.333;bs.inputs['Metallic'].default_value=0
        bs.inputs['Transmission Weight'].default_value=.18;l.new(ramp.outputs[0],bs.inputs['Base Color']);l.new(norm.outputs[0],bs.inputs['Normal'])
        opacity=node('ShaderNodeMapRange',-60,420);opacity.inputs['From Min'].default_value=.2;opacity.inputs['From Max'].default_value=.8;opacity.inputs['To Min'].default_value=.18;opacity.inputs['To Max'].default_value=.8;l.new(h.outputs['Color'],opacity.inputs['Value'])
        tr=node('ShaderNodeBsdfTransparent',180,-160);mix=node('ShaderNodeMixShader',440,100);l.new(opacity.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(bs.outputs[0],mix.inputs[2]);out=node('ShaderNodeOutputMaterial',650,100);l.new(mix.outputs[0],out.inputs[0]);mats.append(m)
    foam=bpy.data.materials.new('W39 | aerated foam');foam.use_nodes=True
    bs=next(n for n in foam.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.8,.92,.95,1);bs.inputs['Roughness'].default_value=.38;bs.inputs['IOR'].default_value=1.333
    paths=[]
    for lane in range(3):
        paths.append([src.data.vertices[lane*612+r*9+4].co.copy() for r in range(68)])
    def ribbon(name,path,width,phase,mat):
        vs=[];uvs=[];faces=[]
        for r,p in enumerate(path):
            t=r/(len(path)-1);w=width*(.78+.17*math.sin(t*27+phase)+.12*math.sin(t*63+phase))
            for j in range(5):
                u=j/4;v=p+Vector(((u-.5)*w,-.025+math.sin(t*32+phase)*.018*math.sin(math.pi*t),.009*math.sin(u*math.pi)*math.sin(math.pi*t)))
                vs.append(v);uvs.append((u,1-t))
            if r:
                for j in range(4):a=(r-1)*5+j;faces.append((a,a+1,a+6,a+5))
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();uv=me.uv_layers.new(name='WaterFlowUV')
        for p in me.polygons:
            p.use_smooth=True
            for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
        o=bpy.data.objects.new(name,me);c.objects.link(o);me.materials.append(mat);return o
    for lane,path in enumerate(paths):
        ribbon('W39 main flow '+str(lane),path,[.59,.29,.2][lane],lane,mats[lane])
        for k in range(4):
            side=-1 if k%2 else 1
            q=[p+Vector((side*(.29+.035*k)*math.sin(math.pi*r/67),-.012*k,0)) for r,p in enumerate(path)]
            ribbon('W39 detached rivulet %d.%d'%(lane,k),q,.018+.006*k,k+lane,mats[(lane+k)%3])
    rng=random.Random(39)
    # Small droplets only: ballistic bursts at the actual lower endpoint.
    base=sum((p[-1] for p in paths),Vector())/3
    for i in range(34):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=base)
        o=bpy.context.object;o.name='W39 splash droplet %02d'%i
        for col in list(o.users_collection):col.objects.unlink(o)
        c.objects.link(o);o.data.materials.append(foam)
        ph=rng.random();ang=rng.uniform(0,math.tau);speed=rng.uniform(.12,.65);rise=rng.uniform(.15,.6);size=rng.uniform(.009,.027)
        q=f'((frame-1)/60.0+{ph})%1.0'
        for axis in range(3):
            dr=o.driver_add('location',axis).driver
            if axis<2:dr.expression=f'{base[axis]}+{speed*(math.cos(ang) if axis==0 else math.sin(ang))}*({q})'
            else:dr.expression=f'{base.z}+{rise}*4*({q})*(1-({q}))'
            o.driver_add('scale',axis).driver.expression=f'{size*(1.8 if axis==2 else 1)}*sin(pi*({q}))'
    # Foam broken into small lobes, not opaque rings spanning the whole fall.
    for end in [0,-1]:
        p=sum((path[end] for path in paths),Vector())/3
        for i in range(22):
            a=rng.uniform(0,math.tau);rad=rng.uniform(.05,.34)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=p+Vector((math.cos(a)*rad,math.sin(a)*rad*.6,.015)))
            o=bpy.context.object;o.name='W39 foam %s.%02d'%(end,i)
            for col in list(o.users_collection):col.objects.unlink(o)
            c.objects.link(o);o.data.materials.append(foam)
            scale=rng.uniform(.02,.055)
            for axis in range(3):o.driver_add('scale',axis).driver.expression=f'{scale*(.4 if axis==2 else 1)}*(1+.17*sin(2*pi*(frame-1)/100+{i}))'
    for name in ['Waterfall_03','Organic cascade foam 2','Organic impact foam 2']:
        ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);ob['W39 preserved source']=True
    s.render.fps=30;s.frame_start=1;s.frame_end=300;s.frame_set(75)
    print('BUILT',len(c.objects),'objects; paths retain source endpoints')

def render_after():
    s=bpy.data.scenes['Scene'];s.camera=bpy.data.objects['W39_PrototypeCamera'];s.render.filepath=ROOT+'/renders/waterfall_after.png'
    bpy.ops.render.render(write_still=True,scene=s.name)

def verify():
    changes=[name for name,d in NS['w39_protected'].items() if signature(bpy.data.objects[name])!=d]
    print('PROTECTED_SIGNATURE_CHANGES',changes)
    print('NEW_DRIVER_COUNT',sum(len(o.animation_data.drivers) if o.animation_data else 0 for o in bpy.data.collections['W39 | Pass A Waterfall Prototype'].objects))

NS['w39_api']={'build':build,'render_after':render_after,'verify':verify}
