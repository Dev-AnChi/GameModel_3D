# -*- coding: utf-8 -*-
"""Stage A: reference proportion reconstruction in the live Blender MCP scene."""
import bpy, math, os, json
from mathutils import Vector
ROOT = r'C:\Game\Commercial_3D\Wandering_Alchemist_v2'
archive = bpy.data.collections.new('ARCHIVE')
bpy.context.scene.collection.children.link(archive)
for obj in list(bpy.context.scene.objects):
    for collection in list(obj.users_collection): collection.objects.unlink(obj)
    if obj.name in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.unlink(obj)
    archive.objects.link(obj)
archive.hide_render = True
archive.hide_viewport = True
rebuild = bpy.data.collections.new('REFERENCE_REBUILD')
bpy.context.scene.collection.children.link(rebuild)
studio = bpy.data.collections.new('REWORK_STUDIO')
bpy.context.scene.collection.children.link(studio)

def material(name, color, roughness=.5, metallic=0):
    m = bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*color,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    return m
oak=material('A_Oak_Honey',(.29,.145,.066),.58)
oaklight=material('A_Oak_Light',(.39,.22,.11),.55)
dark=material('A_Walnut',(.115,.057,.026),.58)
teal=material('A_Deep_Teal',(.027,.135,.132),.86)
ivory=material('A_Warm_Ivory',(.69,.59,.40),.83)
brass=material('A_Antique_Brass',(.39,.265,.102),.38,.75)
iron=material('A_Dark_Iron',(.046,.050,.048),.43,.78)
clay=material('A_Clay',(.44,.44,.44),.73)
potions=[material('A_Liquid_'+str(i),c,.2) for i,c in enumerate([(.08,.49,.51),(.32,.1,.42),(.54,.32,.07),(.10,.32,.16),(.41,.10,.24)])]

def mesh(name, verts, faces, mat, bevel=0, smooth=False):
    data=bpy.data.meshes.new(name+'_Mesh');data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);rebuild.objects.link(obj);data.materials.append(mat)
    if bevel:
        mod=obj.modifiers.new('Edge_Soften','BEVEL');mod.width=bevel;mod.segments=3
    for f in data.polygons:f.use_smooth=smooth
    return obj

def beam(name, start, end, width, depth, mat, bow=.0):
    a,b=Vector(start),Vector(end);direction=(b-a).normalized()
    ref=Vector((0,0,1)) if abs(direction.z)<.95 else Vector((0,1,0))
    u=direction.cross(ref).normalized();v=direction.cross(u).normalized()
    verts=[]
    # Shaped cross-section with clipped corners and slight swelling in mid-span.
    section=[(-1,-.7),(-.7,-1),(.7,-1),(1,-.7),(1,.7),(.7,1),(-.7,1),(-1,.7)]
    for i in range(7):
        t=i/6;center=a.lerp(b,t)+v*(bow*math.sin(math.pi*t));factor=1+.05*math.sin(math.pi*t)
        verts.extend(tuple(center+u*x*width*.5*factor+v*y*depth*.5*factor) for x,y in section)
    faces=[tuple(reversed(range(8))),tuple(range(48,56))]
    faces += [(i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j) for i in range(6) for j in range(8)]
    return mesh(name,verts,faces,mat,.012)

def lathe(name, profile, position, mat, segments=48):
    verts=[]
    for z,r in profile:
        verts.extend((r*math.cos(j*math.tau/segments),r*math.sin(j*math.tau/segments),z) for j in range(segments))
    faces=[tuple(reversed(range(segments)))]
    faces += [(i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j) for i in range(len(profile)-1) for j in range(segments)]
    faces.append(tuple(range((len(profile)-1)*segments,len(profile)*segments)))
    obj=mesh(name,verts,faces,mat,0,True);obj.location=position;return obj

def arc(name, center, rin, rout, thickness, start, end, mat, count=20):
    # True annular sector with depth; axle local Y. Each rim segment is continuous curved geometry.
    verts=[]
    for y in (-thickness/2,thickness/2):
        for r in (rin,rout):
            verts.extend((center[0]+r*math.cos(start+(end-start)*j/count),center[1]+y,center[2]+r*math.sin(start+(end-start)*j/count)) for j in range(count+1))
    n=count+1;faces=[]
    for j in range(count):
        faces.extend([(j,j+1,n+j+1,n+j),(2*n+j,3*n+j,3*n+j+1,2*n+j+1),(j,2*n+j,2*n+j+1,j+1),(n+j,n+j+1,3*n+j+1,3*n+j)])
    faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
    return mesh(name,verts,faces,mat,.007,True)

# Locked proportions: length 5.6, width 2.4, cabin to 3.25; roof crown 4.1.
for y in (-.90,.90): beam('Chassis_Longitudinal',(-2.95,y,1.08),(2.95,y,1.08),.19,.25,dark)
for x in (-2.35,-1.0,.3,1.6,2.35):beam('Floor_Crossbeam',(x,-1.20,1.18),(x,1.20,1.18),.14,.20,dark)
for i in range(12):
    y=-1.1+i*.2
    beam('Floor_Plank_%02d'%i,(-2.82,y,1.37),(2.82,y,1.37),.197,.115,oak if i%3 else oaklight,.008)
for y in (-1.20,1.20):
    for z in (1.52,1.77,2.01):beam('Lower_Side_Plank',(-2.75,y,z),(2.75,y,z),.21,.095,oak,.025)
    beam('Sill_Rail',(-2.90,y,1.32),(2.90,y,1.32),.18,.20,oaklight,.015)
for x in (-2.67,-1.65,1.65,2.67):
    for y in (-1.18,1.18):beam('Cabin_Frame',(x,y,1.38),(x,y,3.25),.15,.17,dark,.025)
# Closed opposite side with actual planks and an open shop front.
for i in range(17):
    x=-2.6+i*.325
    beam('Far_Wall_Plank_%02d'%i,(x,1.19,1.85),(x,1.22,3.40),.315,.075,oak if i%3 else oaklight,.025)
for z in (2.03,3.23):beam('Shop_Rail',(-2.65,-1.19,z),(2.65,-1.19,z),.13,.18,dark)
# Back wall follows the barrel roof; centre arch door remains a separate assembly.
for i in range(9):
    y=-1.13+i*.2825
    top=3.38+.62*math.sqrt(max(0,1-(y/1.25)**2))
    bottom=1.40 if abs(y)>.65 else 3.25
    beam('Rear_Façade_Plank',(2.76,y,bottom),(2.76,y,top),.277,.085,oak,.015)
for i in range(5):
    y=-.52+i*.26;top=2.95+.34*math.sqrt(max(0,1-(y/.67)**2))
    beam('Arched_Door_Plank',(2.82,y,1.44),(2.82,y,top),.249,.09,oaklight,.01)
def pathbeam(name,pts,width,mat):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=width;cu.bevel_resolution=3
    s=cu.splines.new('POLY');s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new(name,cu);rebuild.objects.link(o);cu.materials.append(mat);return o
pts=[(2.89,-.67,1.4),(2.89,-.67,2.96)]
pts += [(2.89,-.67*math.cos(t*math.pi/32),2.96+.42*math.sin(t*math.pi/32)) for t in range(33)]
pts += [(2.89,.67,1.4)]
pathbeam('Rear_Arch_Thick_Frame',pts,.07,dark)
beam('Rear_Step',(3.10,-.8,1.04),(3.10,.8,1.04),.30,.11,oak)

# Wheels are fully connected annular sectors and shaped spokes, not blocks floating in an iron hoop.
for x in (-1.95,1.95):
    beam('Axle',(x,-1.63,.84),(x,1.63,.84),.14,.14,iron)
    for y in (-.9,.9):beam('Axle_Mount',(x,y,.84),(x,y,1.18),.22,.26,iron)
    for y in (-1.48,1.48):
        origin=bpy.data.objects.new('Wheel_Pivot',None);rebuild.objects.link(origin);origin.location=(x,y,.84)
        parts=[]
        for k in range(8):parts.append(arc('Curved_Oak_Felloe',(x,y,.84),.665,.79,.17,k*math.tau/8+.003,(k+1)*math.tau/8-.003,oak if k%2 else oaklight,10))
        parts.append(arc('Iron_Tire',(x,y,.84),.79,.828,.185,0,math.tau,iron,96))
        for k in range(10):
            t=k*math.tau/10
            a=(x+.17*math.cos(t),y,.84+.17*math.sin(t));b=(x+.70*math.cos(t),y,.84+.70*math.sin(t))
            parts.append(beam('Shaped_Wheel_Spoke',a,b,.075,.095,oaklight,.012))
        hub=lathe('Layered_Hub',[(0,.16),(.04,.20),(.10,.20),(.14,.145),(.31,.12),(.36,.085)],(x,y-.18,.84),brass)
        hub.rotation_euler=(math.pi/2,0,0);parts.append(hub)
        for p in parts:world=p.matrix_world.copy();p.parent=origin;p.matrix_world=world
# Pulling shafts angle toward a practical yoke.
for y in (-.58,.58):beam('Tow_Shaft',(-2.72,y,1.18),(-4.65,y*.55,.85),.15,.16,oak,.02)
beam('Tow_Yoke',(-4.55,-.5,.86),(-4.55,.5,.86),.12,.12,dark)

# Continuous barrel canopy with broad gravity sag between ribs, folded over eaves.
xs=[-2.95+5.9*i/80 for i in range(81)]
verts=[];faces=[]
for x in xs:
    for j in range(65):
        t=-1.36+2.72*j/64
        y=1.45*math.sin(t)
        sag=.055*(math.sin((x+2.95)*math.pi/1.475)**2)
        z=3.23+.82*math.cos(t)-sag+.012*math.sin(20*t+2*x)
        verts.append((x,y,z))
for i in range(80):
    for j in range(64):a=i*65+j;faces.append((a,a+65,a+66,a+1))
roof=mesh('Draped_Canopy_Surface',verts,faces,teal,0,True)
mod=roof.modifiers.new('Cloth_Thickness','SOLIDIFY');mod.thickness=.024
for side in (-1,1):
    pts=[(x,side*1.418,3.40-.055*math.sin((x+2.95)*math.pi/1.475)**2) for x in xs]
    pathbeam('Ivory_Roof_Hem',pts,.025,ivory)
# Sheltered lower fabric valance, scalloped edge creating the reference overhang.
for side in (-1,1):
    v=[];f=[]
    for i in range(81):
        x=xs[i]
        for j in range(9):
            t=j/8;z=3.46-t*(.32+.03*math.cos(x*5))
            y=side*(1.42+.07*t+.022*math.sin(x*12)*t)
            v.append((x,y,z))
    for i in range(80):
        for j in range(8):a=i*9+j;f.append((a,a+9,a+10,a+1))
    o=mesh('Scalloped_Canopy_Valance',v,f,teal,0,True);mod=o.modifiers.new('Hem_Thickness','SOLIDIFY');mod.thickness=.016
for x in (-2.80,-1.4,0,1.4,2.80):
    pts=[(x,1.30*math.sin(-1.5+3*j/40),3.20+.77*math.cos(-1.5+3*j/40)) for j in range(41)]
    pathbeam('Under_Canopy_Wood_Rib',pts,.050,dark)
beam('Roof_Ridge',(-3.10,0,4.04),(3.10,0,4.04),.12,.14,dark,.015)

# Broad counter, raised shop shelves and drawer masses: layout stage only.
for j in range(4):beam('Shop_Counter_Plank',(-2.2,-1.25-j*.18,2.05),(2.2,-1.25-j*.18,2.05),.18,.09,oaklight,.008)
for x in (-1.9,1.9):beam('Counter_Support',(x,-1.15,1.45),(x,-1.90,2.01),.095,.12,dark)
for z in (2.04,2.52,3.00):beam('Interior_Display_Shelf',(-2.38,.68,z),(2.38,.68,z),.35,.10,oak)
for x in (-2.24,2.24):
    for z in (2.15,2.36,2.57):beam('Drawer_Mass',(x,-1.23,z),(x,-.70,z),.43,.18,oaklight)
# Ten distinct lathed silhouette studies arranged in clustered depth.
profiles=[[(0,.10),(.03,.15),(.12,.23),(.27,.22),(.36,.08),(.49,.065)],[(0,.10),(.1,.21),(.23,.20),(.39,.10),(.53,.055)],[(0,.12),(.27,.12),(.32,.055),(.66,.055)],[(0,.16),(.25,.16),(.30,.075),(.43,.075)],[(0,.09),(.13,.18),(.28,.1),(.48,.06)],[(0,.12),(.1,.19),(.24,.13),(.36,.18),(.46,.07)],[(0,.16),(.1,.23),(.23,.24),(.34,.10),(.51,.05)],[(0,.1),(.2,.16),(.32,.13),(.43,.07)],[(0,.13),(.12,.20),(.2,.18),(.27,.07),(.52,.07)],[(0,.14),(.08,.22),(.25,.22),(.34,.06),(.62,.045)]]
positions=[(-1.1,-1.53,2.12),(-.68,-1.45,2.12),(-.32,-1.60,2.12),(.17,-1.43,2.12),(.58,-1.62,2.12),(1.0,-1.4,2.12),(-1.7,.60,2.59),(-.7,.60,2.59),(.55,.60,2.59),(1.6,.60,2.59)]
for i,(profile,pos) in enumerate(zip(profiles,positions)):
    lathe('Potion_Silhouette_%02d'%i,profile,pos,potions[i%5],12 if i in (3,4) else 48)
    top=profile[-1][0];lathe('Cork_Study_%02d'%i,[(0,.066),(.08,.068)],(pos[0],pos[1],pos[2]+top),dark,24)
# Lantern silhouettes anchored at eave corners.
for x in (-2.55,2.55):
    for y in (-1.53,1.53):
        pathbeam('Lantern_Hanger',[(x,y*.8,3.45),(x,y,3.44),(x,y,3.15)],.018,iron)
        lathe('Lantern_Silhouette',[(0,.12),(.06,.17),(.28,.15),(.35,.21),(.45,.06)],(x,y,2.72),brass,6)

# White neutral studio with preserved materials; override clay only for actual review render.
scene=bpy.context.scene
scene.world=bpy.data.worlds.new('Rework_Neutral_World');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.32,.32,.32,1);bg.inputs[1].default_value=.4
def area(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
area('Neutral_Key',(-4,-5,8),1500,6);area('Neutral_Fill',(5,-2,6),1100,5);area('Neutral_Rim',(1,5,7),1700,5)
data=bpy.data.cameras.new('Rework_Camera');cam=bpy.data.objects.new('Rework_Camera',data);studio.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=10
floor=mesh('Studio_Ground',[(-200,-200,-.015),(200,-200,-.015),(200,200,-.015),(-200,200,-.015)],[(0,1,2,3)],material('Studio_Grey',(.25,.25,.25),.8));rebuild.objects.unlink(floor);studio.objects.link(floor)
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
out=os.path.join(ROOT,'renders','phase5_rework_stage_a');os.makedirs(out,exist_ok=True)
views={'hero':(-8,-11,7),'side':(0,-13,3.4),'front':(-12,-.2,3.4),'rear':(12,.2,3.4),'rear_threequarter':(9,-10,6)}
def review(mode):
    scene.view_layers[0].material_override=clay if mode=='clay' else None
    for name,pos in views.items():
        cam.location=pos;cam.rotation_euler=(Vector((-.6,0,2.1))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=9.8 if name in ('hero','side','rear_threequarter') else 6.2
        scene.render.filepath=os.path.join(out,mode+'_'+name+'.png');bpy.ops.render.render(write_still=True)
review('clay');review('palette')
scene.view_layers[0].material_override=None
cam.location=views['hero'];cam.rotation_euler=(Vector((-.6,0,2.1))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=9.8
destination=os.path.join(ROOT,'Blender','Wandering_Alchemist_Reference_Rebuild.blend')
bpy.ops.wm.save_as_mainfile(filepath=destination)
print('Saved',destination)
print('Rebuild objects',len(rebuild.objects),'Archived objects',len(archive.objects))
