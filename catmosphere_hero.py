# -*- coding: utf-8 -*-
"""Catmosphere hero reconstruction, executed through Blender MCP."""
import bpy, bmesh, math, random, json
from mathutils import Vector
ROOT='C:/Game/GameModel_3D';NS=bpy.app.driver_namespace
S=bpy.data.scenes['Scene'];random.seed(4109)

def collection(name):
    c=bpy.data.collections.get(name)
    if not c:c=bpy.data.collections.new(name);S.collection.children.link(c)
    return c

def mesh(name,verts,faces,mat,col,uvs=None,smooth=True):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    if mat:me.materials.append(mat)
    for p in me.polygons:p.use_smooth=smooth
    if uvs:
        uv=me.uv_layers.new(name='Hero UV')
        for loop in me.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
    o=bpy.data.objects.new(name,me);col.objects.link(o);return o

def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

def curve(name,points,radius,mat,col):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=2
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    cu.materials.append(mat);o=bpy.data.objects.new(name,cu);col.objects.link(o);return o

def rock(name,center,rx,ry,depth,mat,seed=0,col=None):
    rng=random.Random(seed);N=48;verts=[];faces=[];cx,cy,z=center
    radial=[1+.055*math.sin(a*5+.4*seed)+.035*math.sin(a*9+seed) for a in [2*math.pi*i/N for i in range(N)]]
    for j,(scale,dz) in enumerate([(.86,0),(1,-.12),(1.01,-.30),(.87,-depth*.7),(.43,-depth),(0.10,-depth*1.10)]):
        for i in range(N):
            a=2*math.pi*i/N;r=radial[i]*(1+.025*math.sin(a*11+j))
            verts.append((cx+rx*r*scale*math.cos(a)+.10*j*math.sin(seed),cy+ry*r*scale*math.sin(a),z+dz+(0 if j==0 else .07*math.sin(a*7+seed))))
    faces.append(tuple(reversed(range(N))))
    for j in range(5):
        for i in range(N):a=j*N+i;b=j*N+(i+1)%N;faces.extend([(a,b,b+N),(a,b+N,a+N)])
    faces.append(tuple(5*N+i for i in range(N)))
    ob=mesh(name,verts,faces,mat,col or collection('HERO B | Sculpted limestone'),smooth=False)
    bevel=ob.modifiers.new('Soft weathered ridge edges','BEVEL');bevel.width=.055;bevel.segments=2
    return ob

def pool(name,p,mat):
    cx,cy,z,rx,ry=p;N=96;verts=[(cx,cy,z)];uv=[(.5,.5)]
    for i in range(N):
        a=2*math.pi*i/N;r=1+.025*math.sin(a*5)+.015*math.cos(a*9)
        verts.append((cx+rx*r*math.cos(a),cy+ry*r*math.sin(a),z));uv.append((.5+.5*math.cos(a),.5+.5*math.sin(a)))
    return mesh(name,verts,[(0,i+1,(i+1)%N+1) for i in range(N)],mat,collection('HERO C | Cascade pools'),uv)

def waterfall(name,start,end,width,mat,seed=0):
    start=Vector(start);end=Vector(end);verts=[];faces=[];uv=[];N=72;M=24
    # Overflow rolls outwards before gravity dominates the drop.
    for i in range(N+1):
        t=i/N;fall=t*t*(3-2*t) if t<.15 else t
        p=start.lerp(end,t);p.z=start.z-(start.z-end.z)*(t**1.45)
        p.y-=.42*math.sin(math.pi*min(t*2,1)) if t<.5 else 0
        breadth=width*(1+.07*math.sin(t*9+seed))*(1-.14*t)
        for j in range(M+1):
            u=j/M;edge=2*u-1
            x=p.x+edge*breadth*.5
            y=p.y+.045*math.sin(u*22+t*15+seed)+.023*math.sin(u*51-t*23)
            z=p.z+.018*math.cos(u*20+t*15)*math.sin(math.pi*t)
            verts.append((x,y,z));uv.append((u,t))
    for i in range(N):
        for j in range(M):a=i*(M+1)+j;faces.append((a,a+1,a+M+2,a+M+1))
    o=mesh(name,verts,faces,mat,collection('HERO C | Falling water'),uv)
    sol=o.modifiers.new('Water volume thickness','SOLIDIFY');sol.thickness=.045
    o['hero_start']=list(start);o['hero_end']=list(end);o['hero_width']=width;return o

POOLS=[(3.30,1.15,16.25,1.12,1.03),(3.90,.85,13.05,1.28,1.05),(4.55,.95,9.97,1.40,1.12),(4.55,.65,6.67,1.45,1.08),(5.05,.50,3.49,1.34,1.13),(4.15,-.30,-.28,1.7,1.6)]

def phase_a():
    stone=material('HERO | Blockout warm limestone',(.53,.53,.45),.85)
    water=material('HERO | Blockout turquoise',(.015,.48,.59),.22)
    NS['hero_stone']=stone;NS['hero_water']=water
    for o in list(S.objects):
        name=o.name.lower()
        if name.startswith(('w39 ','r39 ','rel1 ')) and o.type!='CAMERA':o.hide_render=True
        if o.type=='META' and 'cloud' in name:o.hide_render=True
        if o.type in ['MESH','CURVE'] and any(m and any(k in m.name.lower() for k in ['water','foam']) for m in getattr(o.data,'materials',[])):
            if o.name not in ['Ocean basin','Roof pond'] and 'distant' not in name:o.hide_render=True
    for i,p in enumerate(POOLS[:-1]):
        pool('HERO pool '+str(i),p,water)
        rock('HERO pool terrace '+str(i),(p[0],p[1]+.12,p[2]-.17),p[3]*1.18,p[4]*1.15,.95,stone,70+i)
    for i,(a,b) in enumerate(zip(POOLS,POOLS[1:])):
        start=(a[0]+.2,a[1]-a[4]*.83,a[2]);end=(b[0]+.15,b[1]-b[4]*.62,b[2]+.025)
        waterfall('HERO main cascade '+str(i),start,end,.95 if i<2 else 1.2,water,i)
    for i,(start,end,w) in enumerate([((-2.7,-3.55,-.29),(-2.85,-4.0,-4.3),1.10),((.45,-4.22,-.29),(.7,-4.5,-4.9),1.5),((4.50,-1.80,-.29),(4.8,-2.1,-3.9),.8)]):
        waterfall('HERO ocean spill '+str(i),start,end,w,water,i+20)
    for o in S.objects:
        if o.name=='Continuous right natural cliff buttress':o.hide_render=True
    S.camera=bpy.data.objects['HERO | Main portrait camera']
    print('PHASE_A_BLOCKOUT_READY')

def render(name,samples=64,width=756,height=1344,camera=None):
    bpy.context.window.scene=S;S.frame_set(75);S.camera=camera or bpy.data.objects['HERO | Main portrait camera']
    S.render.resolution_x=width;S.render.resolution_y=height;S.eevee.taa_render_samples=samples
    if S.compositing_node_group:
        for node in S.compositing_node_group.nodes:
            if node.bl_idname=='CompositorNodeScale':
                node.inputs['X'].default_value=width/941;node.inputs['Y'].default_value=width/941
    S.render.image_settings.media_type='IMAGE';S.render.image_settings.file_format='PNG';S.render.filepath=ROOT+'/renders/'+name
    bpy.ops.render.render(write_still=True,scene=S.name)

NS['hero_api']={'phase_a':phase_a,'render':render}

def textured_material(name,colors,scale=(4,4,4),rough=.7,bump=.06):
    m=material(name,colors[0],rough);n=m.node_tree.nodes;l=m.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED')
    tc=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=scale;l.new(tc.outputs['Generated'],v.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=3;l.new(v.outputs[0],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*colors[0],1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(*colors[-1],1)
    if len(colors)>2:ramp.color_ramp.elements.new(.5).color=(*colors[1],1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=bump;b.inputs['Distance'].default_value=.03;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal']);return m

def phase_b():
    stone=textured_material('HERO | Sunlit ivory limestone',[(.29,.32,.30),(.53,.54,.46),(.78,.75,.63)],(5,5,7),.82,.14)
    NS['hero_stone']=stone
    oldrocks=[o for o in list(S.objects) if 'Organic primary terrace rock_' in o.name]
    terraces=[]
    for o in oldrocks:
        vs=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector(tuple(min(v[k] for v in vs) for k in range(3)));hi=Vector(tuple(max(v[k] for v in vs) for k in range(3)))
        i=int(o.name[-2:]);center=(lo+hi)/2;z=hi.z-.10
        if i==0:z=-.61
        rx=(hi.x-lo.x)*.51;ry=(hi.y-lo.y)*.49
        rock('HERO terrace limestone '+str(i),(center.x,center.y,z),rx,ry,1.10 if i>0 else 2.7,stone,120+i)
        terraces.append((i,center.x,center.y,z,rx,ry));o.hide_render=True
    NS['hero_terraces']=sorted(terraces)
    bpy.data.objects['Single sculpted sea island foundation'].hide_render=True
    rock('HERO descending island keel',(-.3,.55,-1.75),4.0,2.8,2.65,stone,135)
    for i,(x,y,z,rx,ry,d) in enumerate([(-3.3,.3,-1.3,1.2,1.4,2.5),(2.8,1,-1.6,1.4,1.2,2.25),(-.8,2.2,-1.7,1.6,1.1,2.8)]):rock('HERO hanging limestone buttress '+str(i),(x,y,z),rx,ry,d,stone,160+i)
    for o in list(S.objects):
        if o.type not in ['MESH','CURVE']:continue
        for j,m in enumerate(o.data.materials):
            if m and (('stone' in m.name.lower() and 'fissure' not in m.name.lower() and 'hazy' not in m.name.lower()) or m.name=='HERO | Blockout warm limestone'):o.data.materials[j]=stone
    for o in bpy.data.collections['12 | Fantasy sky and distant islands'].objects:o.hide_render=True
    random.seed(723)
    for i,p in enumerate(POOLS[:-1]):
        for j in range(13):
            a=2*math.pi*j/13
            if -1.95<(a if a<math.pi else a-2*math.pi)<-.95:continue
            r=random.uniform(.12,.22);rock(f'HERO pool {i} bank stone {j}',(p[0]+p[3]*math.cos(a),p[1]+p[4]*math.sin(a),p[2]+.065),r*1.4,r,.18,stone,i*31+j,collection('HERO B | Pool bank details'))
    print('PHASE_B_ROCKS',len(collection('HERO B | Sculpted limestone').objects))

NS['hero_api'].update(phase_b=phase_b)

def mn(n,l,op,a,b=None):
    q=n.new('ShaderNodeMath');q.operation=op
    for i,v in enumerate([a,b]):
        if v is None:continue
        if isinstance(v,(int,float)):q.inputs[i].default_value=v
        else:l.new(v,q.inputs[i])
    return q.outputs[0]

def flow_material():
    m=material('HERO | Turquoise aerated flowing water',(.02,.55,.62),.15);m.surface_render_method='DITHERED';m.use_backface_culling=False
    n=m.node_tree.nodes;l=m.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');out=next(q for q in n if q.type=='OUTPUT_MATERIAL')
    uv=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0])
    mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(.46,1.5,1);l.new(uv.outputs['UV'],mul.inputs[0])
    add=n.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.52,0,0);add.inputs[1].driver_add('default_value',1).driver.expression='-(frame-1)*7/300';l.new(mul.outputs[0],add.inputs[0])
    tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(ROOT+'/textures/water/integration/doodlebuilt_waterfall_fx.png',check_existing=True);tx.image.pack();l.new(add.outputs[0],tx.inputs['Vector'])
    bw=n.new('ShaderNodeRGBToBW');l.new(tx.outputs['Color'],bw.inputs[0]);mask=n.new('ShaderNodeMapRange');mask.inputs['From Min'].default_value=.08;mask.inputs['From Max'].default_value=.48;mask.clamp=True;l.new(bw.outputs[0],mask.inputs['Value'])
    down=mn(n,l,'MULTIPLY_ADD',sep.outputs['Y'],.7);down.node.inputs[2].default_value=.25
    density=mn(n,l,'MULTIPLY',mask.outputs[0],down)
    color=n.new('ShaderNodeMixRGB');color.inputs[1].default_value=(.008,.48,.60,1);color.inputs[2].default_value=(.74,.95,1,1);l.new(density,color.inputs[0]);l.new(color.outputs[0],p.inputs['Base Color'])
    p.inputs['Transmission Weight'].default_value=.19;p.inputs['IOR'].default_value=1.333;p.inputs['Emission Color'].default_value=(.012,.40,.46,1);p.inputs['Emission Strength'].default_value=.12
    nu=n.new('ShaderNodeVectorMath');nu.operation='MULTIPLY';nu.inputs[1].default_value=(2.5,5,1);l.new(uv.outputs['UV'],nu.inputs[0]);na=n.new('ShaderNodeVectorMath');na.operation='ADD';l.new(nu.outputs[0],na.inputs[0]);na.inputs[1].driver_add('default_value',1).driver.expression='-(frame-1)*19/300'
    nt=n.new('ShaderNodeTexImage');nt.image=bpy.data.images['normal.png'];l.new(na.outputs[0],nt.inputs[0]);nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.30;l.new(nt.outputs['Color'],nm.inputs['Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.04;l.new(bw.outputs[0],bump.inputs['Height']);l.new(nm.outputs[0],bump.inputs['Normal']);l.new(bump.outputs[0],p.inputs['Normal'])
    edge=mn(n,l,'MINIMUM',sep.outputs['X'],mn(n,l,'SUBTRACT',1,sep.outputs['X']));opacity=n.new('ShaderNodeMapRange');opacity.inputs['From Min'].default_value=.003;opacity.inputs['From Max'].default_value=.055;opacity.clamp=True;l.new(edge,opacity.inputs['Value'])
    tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(opacity.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
    m['texture_source']='doodlebuilt Toon Waterfall CC0; ProcTexture wave normal CC0';return m

def pool_material():
    m=material('HERO | Luminous turquoise pools',(.016,.53,.59),.17);n=m.node_tree.nodes;l=m.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.18
    uv=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=14;noise.inputs['Detail'].default_value=3;l.new(uv.outputs['Generated'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.008,.30,.37,1);ramp.color_ramp.elements[1].color=(.20,.82,.77,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.18;b.inputs['Distance'].default_value=.025;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal']);p.inputs['Emission Color'].default_value=(.015,.40,.45,1);p.inputs['Emission Strength'].default_value=.14
    return m

def foam_material():
    m=material('HERO | Soft cellular whitewater',(.85,.97,1),.40);m.surface_render_method='DITHERED';n=m.node_tree.nodes;l=m.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');out=next(q for q in n if q.type=='OUTPUT_MATERIAL')
    uv=n.new('ShaderNodeTexCoord');sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,0);l.new(uv.outputs['UV'],sub.inputs[0]);dist=n.new('ShaderNodeVectorMath');dist.operation='LENGTH';l.new(sub.outputs[0],dist.inputs[0]);rad=n.new('ShaderNodeMapRange');rad.inputs['From Min'].default_value=.22;rad.inputs['From Max'].default_value=.50;rad.inputs['To Min'].default_value=.95;rad.inputs['To Max'].default_value=0;rad.clamp=True;l.new(dist.outputs['Value'],rad.inputs['Value'])
    noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=3;noise.inputs['W'].driver_add('default_value').driver.expression='.4*sin(2*pi*(frame-1)*3/300)';l.new(uv.outputs['UV'],noise.inputs[0]);cut=n.new('ShaderNodeMapRange');cut.inputs['From Min'].default_value=.33;cut.inputs['From Max'].default_value=.60;cut.clamp=True;l.new(noise.outputs['Fac'],cut.inputs['Value'])
    a=mn(n,l,'MULTIPLY',rad.outputs[0],cut.outputs[0]);tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(a,mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface']);return m

def ico(name,loc,scale,mat,col,sub=2):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    o=bpy.data.objects.new(name,me);col.objects.link(o);o.location=loc;o.scale=scale;return o

def phase_c():
    water=flow_material();lake=pool_material();foam=foam_material();spray=material('HERO | Airborne water glints',(.64,.93,1),.13)
    NS['hero_water']=water;NS['hero_lake']=lake;NS['hero_foam']=foam
    for o in collection('HERO C | Falling water').objects:o.data.materials[0]=water
    for o in collection('HERO C | Cascade pools').objects:o.data.materials[0]=lake
    for name in ['Ocean basin','Roof pond']:
        o=bpy.data.objects[name];o.data.materials.clear();o.data.materials.append(lake)
    # Two secondary branches, each landing inside an intermediate pool.
    waterfall('HERO secondary bedroom cascade',(5.35,.40,9.97),(5.35,-.10,6.72),.34,water,44)
    waterfall('HERO secondary lounge cascade',(3.25,.20,13.04),(4.10,.40,10.01),.29,water,45)
    detail=collection('HERO C | Impact foam and spray');random.seed(991)
    for i,p in enumerate(POOLS[1:]):
        cx=p[0]+.15;cy=p[1]-p[4]*.62;z=p[2]+.045
        for j in range(3):pool(f'HERO impact whitewater {i}-{j}',(cx+random.uniform(-.25,.25),cy+random.uniform(-.18,.18),z+.006*j,.52+random.random()*.2,.38+random.random()*.2),foam)
        for j in range(5):
            a=j*2.4+i;dx=.22*math.cos(a);dy=.22*math.sin(a);curve(f'HERO splash arc {i}-{j}',[(cx,cy,z),(cx+dx*.5,cy+dy*.5,z+.15+random.random()*.12),(cx+dx,cy+dy,z+.015)],.009,spray,detail)
        for j in range(18):
            o=ico(f'HERO spray particle {i}-{j}',(cx,cy,z),(.012,.012,.025),spray,detail,1);phase=random.random();period=random.choice([50,60,75,100]);age=f'(((frame-1)/{period}+{phase})%1)';a=random.random()*math.tau;distance=random.uniform(.2,.6);height=random.uniform(.15,.45)
            for k,expr in enumerate([f'{cx}+{distance*math.cos(a)}*{age}',f'{cy}+{distance*math.sin(a)}*{age}',f'{z}+4*{height}*{age}*(1-{age})']):o.driver_add('location',k).driver.expression=expr
            for k,base in enumerate([.012,.012,.026]):o.driver_add('scale',k).driver.expression=f'{base}*sin(pi*{age})'
    # Shoreline gleams remain broken and shallow, rather than large white rings.
    for i,p in enumerate(POOLS[:-1]):
        for j in range(5):
            a=.3+j*.5;points=[(p[0]+p[3]*.86*math.cos(a+k*.035),p[1]+p[4]*.86*math.sin(a+k*.035),p[2]+.015) for k in range(5)]
            curve(f'HERO broken pool gleam {i}-{j}',points,.009,spray,detail)
    print('PHASE_C_MULTITIER_WATER_READY')

NS['hero_api'].update(phase_c=phase_c)
