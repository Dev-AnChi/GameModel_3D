# -*- coding: utf-8 -*-
"""Botanical borders and atmospheric material polish for the hero scene."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
NS=bpy.app.driver_namespace
G=NS['hero_api']['render'].__globals__
collection=G['collection'];mesh=G['mesh'];material=G['material'];curve=G['curve'];ico=G['ico'];textured_material=G['textured_material'];S=G['S'];POOLS=G['POOLS']

def fix_rock_seating():
    for o in collection('HERO B | Sculpted limestone').objects:
        if o.name.startswith('HERO terrace limestone '):
            i=int(o.name.rsplit(' ',1)[-1])
            if i:
                target={1:3.11,2:6.31,3:9.51,4:12.71,5:15.91}[i];delta=target-max(v.co.z for v in o.data.vertices)
                for v in o.data.vertices:v.co.z+=delta
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for o in collection('HERO B | Pool bank details').objects:
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for o in collection('HERO C | Falling water').objects:
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    terraces=[]
    for i,cx,cy,z,rx,ry in NS['hero_terraces']:
        if i:z={1:3.11,2:6.31,3:9.51,4:12.71,5:15.91}[i]
        terraces.append((i,cx,cy,z,rx,ry))
    NS['hero_terraces']=terraces

class Plants:
    def __init__(self,mats):self.v=[];self.f=[];self.indices=[];self.mats=mats
    def polygon(self,vs,faces,idx):
        base=len(self.v);self.v.extend(vs);self.f.extend([tuple(base+i for i in f) for f in faces]);self.indices.extend([idx]*len(faces))
    def leaf(self,p,a,tilt,length,idx):
        rot=Matrix.Rotation(a,3,'Z')@Matrix.Rotation(tilt,3,'X');p=Vector(p);vs=[]
        for j in range(7):
            t=j/6;w=length*.22*math.sin(math.pi*t)**.8
            for x in [-w,0,w]:vs.append(tuple(p+rot@Vector((x,length*t,.07*math.sin(math.pi*t)+abs(x)*.14))))
        faces=[]
        for j in range(6):
            for k in range(2):i=j*3+k;faces.append((i,i+1,i+4,i+3))
        self.polygon(vs,faces,idx)
    def flower(self,head,r,idx):
        head=Vector(head)
        for petal in range(5):
            a=petal*math.tau/5;d=Vector((math.cos(a),math.sin(a),0));cross=Vector((-math.sin(a),math.cos(a),0));center=head+d*r*.70;vs=[tuple(center+Vector((0,0,-r*.12)))]
            for j in range(10):
                b=j*math.tau/10;vs.append(tuple(center+d*(r*.71*math.cos(b))+cross*(r*.48*math.sin(b))+Vector((0,0,r*.18*math.cos(b)**2))))
            self.polygon(vs,[(0,j+1,(j+1)%10+1) for j in range(10)],idx)
        self.polygon([tuple(head+Vector(v)*r*.30) for v in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,.6),(0,0,-.1)]],[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)],7)
    def stem(self,start,end):
        p=Vector(start);q=Vector(end);direction=(q-p).normalized();u=direction.cross(Vector((1,0,0))).normalized();v=direction.cross(u);vs=[]
        for center in [p,q]:
            for i in range(5):a=i*math.tau/5;vs.append(tuple(center+.005*(u*math.cos(a)+v*math.sin(a))))
        self.polygon(vs,[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)],0)
    def finish(self,name,col):
        o=mesh(name,self.v,self.f,None,col)
        for m in self.mats:o.data.materials.append(m)
        for p,i in zip(o.data.polygons,self.indices):p.material_index=i
        return o

def make_plant_materials():
    colors=[(.035,.16,.015),(.11,.31,.018),(.27,.48,.036),(.82,.11,.29),(.92,.84,.66),(.46,.17,.65),(.70,.30,.48),(.96,.45,.018)]
    mats=[]
    for i,c in enumerate(colors):
        m=material('HERO | Botanical palette '+str(i),c,.50 if i<3 else .43);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Subsurface Weight'].default_value=.065 if i<7 else 0;mats.append(m)
    return mats

def phase_d():
    fix_rock_seating();mats=make_plant_materials();NS['hero_plant_mats']=mats;col=collection('HERO D | Botanical borders');vines=collection('HERO D | Hanging vines');random.seed(6801)
    dg=bpy.context.evaluated_depsgraph_get();trees=[]
    for o in list(collection('HERO B | Sculpted limestone').objects)+list(collection('HERO B | Pool bank details').objects):
        ev=o.evaluated_get(dg);me=ev.to_mesh();trees.append(BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]));ev.to_mesh_clear()
    def ground(p):
        hits=[]
        for t in trees:
            h,*_=t.ray_cast(Vector((p[0],p[1],p[2]+.50)),Vector((0,0,-1)),1.0)
            if h:hits.append(h.z)
        return max(hits)+.014 if hits else p[2]
    def shrub(name,p,r=.45,count=18,on_rock=True):
        p=Vector(p)
        if on_rock:p.z=ground(p)
        b=Plants(mats)
        for j in range(count*3):
            a=random.random()*math.tau;rr=r*math.sqrt(random.random());root=p+Vector((rr*math.cos(a),rr*math.sin(a),.02));b.leaf(root,a+random.uniform(-1,1),random.uniform(.30,1.00),random.uniform(.21,.41),random.randrange(3))
        for j in range(count):
            a=random.random()*math.tau;rr=r*.85*math.sqrt(random.random());root=p+Vector((rr*math.cos(a),rr*math.sin(a),0));head=root+Vector((random.uniform(-.04,.04),random.uniform(-.04,.04),random.uniform(.22,.46)));b.stem(root,head);b.flower(head,random.uniform(.045,.071),random.choices([3,4,5,6],[5,6,1,3])[0])
        return b.finish(name,col)
    def vine(name,p,length):
        p=Vector(p);points=[];b=Plants(mats);phase=random.random()*6
        for j in range(28):
            t=j/27;q=p+Vector((.16*math.sin(t*6+phase)*t,-.10-.18*t+.07*math.sin(t*8),-length*t));points.append(tuple(q))
            for side in [-1,1]:b.leaf(q,side*1.2+.3*math.sin(j),random.uniform(-.4,.5),random.uniform(.12,.23),random.randrange(3))
            if j%5==1:b.flower(q+Vector((.05,-.03,.035)),.045,random.choice([3,4,6]))
        curve(name+' stem',points,.009,mats[0],vines);b.finish(name+' leaves and blossoms',vines)
    for i,cx,cy,z,rx,ry in NS['hero_terraces']:
        if i==0:continue
        for j,a in enumerate([.15,.55,1.6,2.9,3.4,3.9,4.35,4.85,5.40,5.85]):
            p=(cx+rx*.93*math.cos(a),cy+ry*.93*math.sin(a),z-.04);shrub(f'HERO tier {i} flower border {j}',p,.48+random.random()*.18,20)
            if j in [3,5,7,9]:vine(f'HERO tier {i} trailing garden {j}',(p[0],p[1],ground(p)),random.uniform(1.25,2.35))
    for i,p in enumerate(POOLS[:-1]):
        for j,a in enumerate([.1,.7,1.3,2.0,2.7,3.3,4.2,5.6]):
            root=(p[0]+p[3]*1.04*math.cos(a),p[1]+p[4]*1.04*math.sin(a),p[2]);shrub(f'HERO pool {i} flowering bank {j}',root,.32,13)
            if j in [0,4,7]:vine(f'HERO pool {i} hanging garland {j}',(root[0],root[1],ground(root)),random.uniform(.85,1.5))
    for j in range(8):
        x=-3.25+j*.50;shrub(f'HERO pergola rose crown {j}',(x,.77,19.25),.36,15,False)
        if j in [0,2,5,7]:vine(f'HERO pergola floral drape {j}',(x,.68,19.22),random.uniform(1.55,2.50))
    for j,p in enumerate([(-4.5,-1.6,.3),(-4.2,.5,.34),(3.8,-2.15,.17),(3.3,1.8,.08),(-3.0,-2.7,.3)]):shrub('HERO beach hydrangea bed '+str(j),p,.65,26,False)
    # Secondary tree crowns amplify the left silhouette without filling the rooms.
    for j,p in enumerate([(-5.1,.6,11.1),(-4.8,1.0,10.7),(-4.3,.7,11.3),(-4.7,1.5,11.55)]):shrub('HERO left tree flowering crown '+str(j),p,.72,19,False)
    print('PHASE_D_GARDENS',len(col.objects),'VINES',len(vines.objects))

def phase_e():
    warm=textured_material('HERO | Honey oak structural',[(.23,.085,.023),(.45,.22,.070),(.62,.36,.13)],(3,50,3),.44,.055)
    floor=textured_material('HERO | Warm teak floorboards',[(.27,.11,.029),(.46,.23,.074),(.63,.37,.15)],(3,70,3),.47,.04)
    trim=material('HERO | Golden timber edges',(.52,.29,.095),.40)
    for o in list(S.objects):
        if o.type not in ['MESH','CURVE']:continue
        for i,m in enumerate(o.data.materials):
            if not m or m.name.startswith('HERO'):continue
            name=m.name.lower()
            if 'wood' in name and not any(k in name for k in ['bark','dark']):o.data.materials[i]=floor if 'floorboard' in name else trim if 'trim' in name else warm
            elif 'greenhouse sage' in name:o.data.materials[i]=warm
            elif 'leaf' in name:o.data.materials[i]=NS['hero_plant_mats'][2 if 'golden' in name else 1 if 'fresh' in name else 0]
            elif 'pink blossoms' in name:o.data.materials[i]=NS['hero_plant_mats'][6]
            elif 'ivory blossoms' in name:o.data.materials[i]=NS['hero_plant_mats'][4]
    sun=bpy.data.objects['Warm sunlight'];sun.data.energy=3.0;sun.data.color=(1,.91,.74);sun.data.angle=math.radians(12)
    key=bpy.data.objects['Large soft key'];key.data.energy=2100;key.data.shape='DISK';key.data.size=12;key.data.color=(1,.94,.84)
    fill=bpy.data.objects['Sky bounce front'];fill.data.energy=1500;fill.data.size=14;fill.data.color=(.80,.90,1)
    rim=bpy.data.objects['Beauty golden foliage rim'];rim.data.energy=1500;rim.data.color=(1,.86,.62)
    world=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');world.inputs['Color'].default_value=(.63,.79,1,1);world.inputs['Strength'].default_value=.42
    S.view_settings.exposure=.35
    looks=[e.identifier for e in S.view_settings.bl_rna.properties['look'].enum_items]
    if 'AgX - Medium High Contrast' in looks:S.view_settings.look='AgX - Medium High Contrast'
    for n in S.compositing_node_group.nodes:
        if n.bl_idname=='CompositorNodeScale':n.inputs['X'].default_value=756/941;n.inputs['Y'].default_value=756/941
    S.frame_start=1;S.frame_end=300;S.render.fps=30
    # Restrained volumetric mist at open-air waterfall terminations.
    m=bpy.data.materials.new('HERO | Soft waterfall mist');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.90,.96,1,1);vol.inputs['Density'].default_value=.085
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=2;uv=n.new('ShaderNodeTexCoord');l.new(uv.outputs['Generated'],noise.inputs[0]);mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';mult.inputs[1].default_value=.13;l.new(noise.outputs['Fac'],mult.inputs[0]);l.new(mult.outputs[0],vol.inputs['Density']);l.new(vol.outputs[0],out.inputs['Volume'])
    col=collection('HERO E | Mist and atmosphere')
    for i,p in enumerate([(-2.85,-4,-4.15),(.7,-4.5,-4.7),(4.8,-2.1,-3.75)]):ico('HERO waterfall vapor '+str(i),p,(.75,.6,.42),m,col,3)
    print('PHASE_E_MATERIAL_LIGHTING_READY')

NS['hero_api'].update(phase_d=phase_d,phase_e=phase_e)
