# -*- coding: utf-8 -*-
import bpy,os,json,math
from mathutils import Vector
ROOT=r'C:\Game\GameModel_3D\Wandering_Alchemist_v2'
with open(os.path.join(ROOT,'textures','downloaded','verified_manifest.json'),encoding='utf-8') as f:assets={a['id']:a for a in json.load(f)}
for path in ('renders/material_tests','renders/hero','renders/closeups','textures/baked','reports'):os.makedirs(os.path.join(ROOT,path),exist_ok=True)
main=bpy.context.scene
def pbr(name,asset,tint=None,metallic=0,normal_strength=.25):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED')
    p.inputs['Metallic'].default_value=metallic
    texcoord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');l.new(texcoord.outputs['UV'],mapping.inputs['Vector'])
    if asset=='oak_veneer_01':mapping.inputs['Rotation'].default_value[2]=math.pi/2
    if asset=='rough_linen':mapping.inputs['Scale'].default_value=(1,1,1)
    for role in ('Diffuse','Rough','nor_gl'):
        im=bpy.data.images.load(assets[asset]['files'][role]['path'],check_existing=True)
        im.colorspace_settings.name='sRGB' if role=='Diffuse' else 'Non-Color'
        assert im.size[0]>0
        node=n.new('ShaderNodeTexImage');node.image=im;node.label=asset+' '+role;l.new(mapping.outputs['Vector'],node.inputs['Vector'])
        if role=='Diffuse':
            if tint:
                bw=n.new('ShaderNodeRGBToBW');ramp=n.new('ShaderNodeValToRGB');l.new(node.outputs['Color'],bw.inputs[0]);l.new(bw.outputs[0],ramp.inputs[0])
                ramp.color_ramp.elements[0].position=.05;ramp.color_ramp.elements[0].color=(*[v*.50 for v in tint],1)
                ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(*tint,1);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
            else:l.new(node.outputs['Color'],p.inputs['Base Color'])
        elif role=='Rough':
            r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.25 if metallic else .65 if asset=='rough_linen' else .35;r.inputs['To Max'].default_value=.55 if metallic else .90 if asset=='rough_linen' else .62;l.new(node.outputs[0],r.inputs['Value']);l.new(r.outputs[0],p.inputs['Roughness'])
        else:
            normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=normal_strength;l.new(node.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
    return m
wood=pbr('P65A_Oak_Trial','oak_veneer_01',(.38,.215,.092),0,.27)
cloth=pbr('P65A_Teal_Linen_Trial','rough_linen',(.020,.105,.092),0,.85)
next(n for n in cloth.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Sheen Weight'].default_value=.25
brass=pbr('P65A_Antique_Brass_Trial','metal_plate_02',(.46,.31,.12),1,.10)
glass=bpy.data.materials.new('P65A_Potion_Glass');glass.use_nodes=True
p=next(q for q in glass.node_tree.nodes if q.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.96,.99,1,1);p.inputs['Roughness'].default_value=.045;p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46
liquid=bpy.data.materials.new('P65A_Cyan_Elixir');liquid.use_nodes=True
p=next(q for q in liquid.node_tree.nodes if q.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.03,.46,.48,1);p.inputs['Roughness'].default_value=.06;p.inputs['Transmission Weight'].default_value=.85;p.inputs['IOR'].default_value=1.33
volume=liquid.node_tree.nodes.new('ShaderNodeVolumeAbsorption');volume.inputs['Color'].default_value=(.08,.62,.70,1);volume.inputs['Density'].default_value=.8
out=next(q for q in liquid.node_tree.nodes if q.type=='OUTPUT_MATERIAL');liquid.node_tree.links.new(volume.outputs[0],out.inputs['Volume'])
def lathe(name,profile,pos,mat,collection):
    count=64;verts=[(r*math.cos(j*math.tau/count),r*math.sin(j*math.tau/count),z) for z,r in profile for j in range(count)]
    faces=[tuple(reversed(range(count)))];faces += [(i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j) for i in range(len(profile)-1) for j in range(count)];faces.append(tuple(range((len(profile)-1)*count,len(profile)*count)))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);obj=bpy.data.objects.new(name,me);collection.objects.link(obj);obj.location=pos;me.materials.append(mat)
    for face in me.polygons:face.use_smooth=len(face.vertices)==4
    return obj
shell_profile=[(0,.075),(.02,.12),(.08,.18),(.18,.205),(.29,.18),(.36,.1),(.41,.06),(.56,.06),(.57,.074),(.595,.074),(.595,.046),(.56,.046),(.41,.046),(.36,.087),(.29,.166),(.18,.19),(.08,.166),(.035,.105),(.035,0)]
liquid_profile=[(.045,.07),(.075,.153),(.18,.177),(.26,.168),(.275,.166),(.268,.13),(.268,0)]

# Dedicated scene, not a pile of test objects beside the caravan.
test=bpy.data.scenes.new('PHASE65A_MATERIAL_TEST');test.world=bpy.data.worlds.new('Material_Test_Neutral');test.world.use_nodes=True
bg=next(n for n in test.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.28,.28,.28,1);bg.inputs[1].default_value=.45
test.render.engine='CYCLES';test.cycles.samples=40;test.cycles.use_denoising=True;test.cycles.max_bounces=10;test.cycles.transmission_bounces=8
test.render.resolution_x=1500;test.render.resolution_y=800;test.render.resolution_percentage=100
collection=test.collection
def relink(obj):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    collection.objects.link(obj)
def cube(name,loc,scale,mat):
    verts=[(x*scale[0],y*scale[1],z*scale[2]) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);o=bpy.data.objects.new(name,me);collection.objects.link(o);o.location=loc;me.materials.append(mat)
    uv=me.uv_layers.new()
    for face in me.polygons:
        for li,co in zip(face.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
    b=o.modifiers.new('Soft_Edges','BEVEL');b.width=.035;b.segments=3;return o
grey=bpy.data.materials.new('Test_Ground');grey.use_nodes=True;next(n for n in grey.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.18,.18,.18,1)
cube('Oak_Test_Plank',(-2.1,0,.35),(.65,.30,.30),wood)
v=[];f=[]
for i in range(49):
    for j in range(41):
        x=-.65+1.3*i/48;y=-.36+.72*j/40;v.append((x-.6,y,.56+.055*math.cos(i/48*math.pi*6)+.11*math.sin(j/40*math.pi)))
for i in range(48):
    for j in range(40):a=i*41+j;f.append((a,a+41,a+42,a+1))
me=bpy.data.meshes.new('Linen_Drape');me.from_pydata(v,[],f);o=bpy.data.objects.new('Teal_Linen_Test_Drape',me);collection.objects.link(o);me.materials.append(cloth);uv=me.uv_layers.new()
for face in me.polygons:
    face.use_smooth=True
    for li in face.loop_indices:
        vi=me.loops[li].vertex_index;uv.data[li].uv=(vi//41/48,vi%41/40)
o.modifiers.new('Cloth_Thickness','SOLIDIFY').thickness=.02
o=lathe('Antique_Brass_Test',[(.4+.4*math.cos(math.pi*k/32),max(.0001,.4*math.sin(math.pi*k/32))) for k in range(33)],(.9,0,.07),brass,collection)
uv=o.data.uv_layers.new()
for face in o.data.polygons:
    for li in face.loop_indices:
        vi=o.data.loops[li].vertex_index;uv.data[li].uv=(vi%64/64,vi//64/32)
lathe('Glass_Test_Shell',shell_profile,(2.2,0,.06),glass,collection);lathe('Glass_Test_Liquid',liquid_profile,(2.2,0,.06),liquid,collection)
lathe('Glass_Test_Cork',[(0,.049),(.08,.053)],(2.2,0,.64),bpy.data.materials['P6_Dark_Walnut'],collection)
cube('Neutral_Ground',(0,0,-.06),(100,100,.06),grey)
for x,label in [(-2.1,'OAK'),(-.6,'TEAL LINEN'),(.9,'ANTIQUE BRASS'),(2.2,'GLASS + LIQUID')]:
    cu=bpy.data.curves.new(label,'FONT');cu.body=label;cu.size=.12;cu.align_x='CENTER';o=bpy.data.objects.new(label,cu);collection.objects.link(o);o.location=(x,-.60,.015)
for name,pos,energy,size in [('Key',(-2,-3,5),650,4),('Fill',(3,-1,3),400,3),('Reflect_Strip',(1,3,4),900,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.size=size;o=bpy.data.objects.new(name,data);collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Test_Camera');camera=bpy.data.objects.new('Test_Camera',data);collection.objects.link(camera);test.camera=camera;data.type='ORTHO';data.ortho_scale=6.7;camera.location=(2,-7,5);camera.rotation_euler=(Vector((0,0,.3))-camera.location).to_track_quat('-Z','Y').to_euler()
test.render.filepath=os.path.join(ROOT,'renders','material_tests','four_material_board.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Blender','Wandering_Alchemist_Phase6_5_Premium.blend'))
bpy.ops.render.render(write_still=True,scene=test.name)
print('Material test board saved; next step trial assignment only.')
