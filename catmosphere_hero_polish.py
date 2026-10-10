# -*- coding: utf-8 -*-
import bpy,bmesh,math,random
from mathutils import Vector
NS=bpy.app.driver_namespace;G=NS['hero_api']['render'].__globals__;S=G['S'];rock=G['rock'];collection=G['collection'];curve=G['curve'];material=G['material']

def phase_f():
    random.seed(41017);stone=NS['hero_stone'];col=collection('HERO F | Cliff shoulders and details')
    for i,cx,cy,z,rx,ry in NS['hero_terraces']:
        if not i:continue
        for j,a in enumerate([3.15,3.6,4.0,4.5,4.95,5.4,5.8]):
            x=cx+rx*.90*math.cos(a);y=cy+ry*.94*math.sin(a)
            r=random.uniform(.28,.48);o=rock(f'HERO carved terrace shoulder {i}-{j}',(x,y,z-.19),r*1.55,r*.92,random.uniform(.45,.72),stone,i*123+j,col)
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for o in S.objects:
        if o.name.startswith('Master sea-cliff bonded outcrop_'):o.hide_render=True
    o=bpy.data.objects['HERO terrace limestone 0'];center=Vector((-.131, -.198,0))
    for v in o.data.vertices:
        ring=v.index//48
        if ring>=3:
            scale={3:.70,4:.63,5:.5}[ring];v.co.x=center.x+(v.co.x-center.x)*scale;v.co.y=center.y+(v.co.y-center.y)*scale
    o=rock('HERO front tapered island root',(-1.05,-1.2,-1.40),2.6,1.9,3.05,stone,923,col)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    bark=material('HERO | Mature tree bark',(.15,.072,.026),.72)
    for j,p in enumerate([(-5.1,.6,11.1),(-4.8,1,10.7),(-4.3,.7,11.3),(-4.7,1.5,11.55)]):curve('HERO crown supporting branch '+str(j),[(-4.0,1.5,8.6),(-4.3,1.1,10.1),p],.045,bark,col)
    bpy.data.objects['Warm sunlight'].data.energy=2.5;bpy.data.objects['Large soft key'].data.energy=1700;bpy.data.objects['Sky bounce front'].data.energy=1000;bpy.data.objects['Beauty golden foliage rim'].data.energy=1900
    world=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');world.inputs['Strength'].default_value=.32;S.view_settings.exposure=.12
    for name in ['HERO | Honey oak structural','HERO | Warm teak floorboards']:
        m=bpy.data.materials[name];r=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeValToRGB')
        for e in r.color_ramp.elements:
            c=e.color;e.color=(c[0]*.88,c[1]*.78,c[2]*.74,1)
    m=NS['hero_stone'];r=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeValToRGB')
    for e in r.color_ramp.elements:
        c=e.color;e.color=(c[0]*.90,c[1]*.90,c[2]*.92,1)
    # Floating-island spill ends break into vapor instead of a straight sheet edge.
    for o in collection('HERO C | Falling water').objects:
        if not o.name.startswith('HERO ocean spill'):continue
        mat=o.data.materials[0].copy();mat.name='HERO | Airborne taper '+o.name[-1];o.data.materials[0]=mat;n=mat.node_tree.nodes;l=mat.node_tree.links
        sep=next(q for q in n if q.bl_idname=='ShaderNodeSeparateXYZ');mix=next(q for q in n if q.bl_idname=='ShaderNodeMixShader');original=mix.inputs[0].links[0].from_socket
        fade=n.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.75;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;fade.clamp=True;l.new(sep.outputs['Y'],fade.inputs['Value'])
        multiply=n.new('ShaderNodeMath');multiply.operation='MULTIPLY';l.new(original,multiply.inputs[0]);l.new(fade.outputs[0],multiply.inputs[1]);l.new(multiply.outputs[0],mix.inputs[0])
    targets={'rooftop':((-0.6,.8,17.5),10.0),'lounge':((-.6,.6,13.8),9.1),'bedroom':((.7,.4,10.5),9.2),'dining':((1.7,-.1,4.2),10.0),'beach':((0,-.65,.35),13.0)}
    cams={}
    for key,(point,scale) in targets.items():
        d=bpy.data.cameras.new('HERO close-up '+key);o=bpy.data.objects.new(d.name,d);S.collection.objects.link(o);target=Vector(point);o.location=target+Vector((14,-27,13));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;cams[key]=o
    NS['hero_closeup_cameras']=cams
    print('PHASE_F_POLISH_READY')

NS['hero_api']['phase_f']=phase_f
