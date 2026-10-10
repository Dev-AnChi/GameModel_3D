# -*- coding: utf-8 -*-
import bpy, os, math
from mathutils import Vector
R=r"C:\Game\Commercial_3D\Wandering_Alchemist_v2"
for d in ("Blender",os.path.join("Preview","Phase_1"),"Documentation","Props","Textures","Exports"):os.makedirs(os.path.join(R,d),exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def M(n,c,e=0,met=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes["Principled BSDF"];p.inputs["Base Color"].default_value=(*c,1);p.inputs["Roughness"].default_value=.42;p.inputs["Metallic"].default_value=met
 if e:p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=e
 return m
wood=M("Honey Wood",(.28,.07,.02));light=M("Light Wood",(.55,.19,.04));brass=M("Aged Brass",(.5,.23,.04),0,.75);iron=M("Forged Iron",(.04,.05,.06),0,.8);teal=M("Teal Canvas",(.01,.22,.2));cyan=M("Cyan Potion",(0,.35,.45),4);pink=M("Pink Potion",(.55,.01,.15),4);purple=M("Lavender",(.26,.03,.35));moss=M("Moss",(.02,.2,.06));ground=M("Ground",(.02,.035,.03))
def style(o,m,b=.04):
 o.data.materials.append(m)
 if b:x=o.modifiers.new("Bevel","BEVEL");x.width=b;x.segments=3
 return o
def B(n,p,s,m=wood,r=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(location=p,rotation=r);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return style(o,m)
def C(n,p,rad,d,m=wood,r=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=18,radius=rad,depth=d,location=p,rotation=r);o=bpy.context.object;o.name=n;return style(o,m,.025)
def S(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=18,ring_count=10,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return style(o,m,.015)
def T(n,p,a,b,m,r=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=a,minor_radius=b,major_segments=24,minor_segments=8,location=p,rotation=r);o=bpy.context.object;o.name=n;return style(o,m)
def Q(n,pts,w,m):
 c=bpy.data.curves.new(n,"CURVE");c.dimensions="3D";c.bevel_depth=w;c.bevel_resolution=3;s=c.splines.new("BEZIER");s.bezier_points.add(len(pts)-1)
 for x,p in zip(s.bezier_points,pts):x.co=p;x.handle_left_type="AUTO";x.handle_right_type="AUTO"
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(m)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
B("Chassis",(0,0,1.65),(3.45,1.25,.28),wood);B("Undercarriage",(0,0,1.33),(3.8,.78,.17),iron)
for x in (-2.75,2.7):
 C("Axle",(x,0,1.02),.14,3.35,iron,(math.pi/2,0,0))
 for y in (-1.48,1.48):
  C("Wheel",(x,y,1),.92,.22,light,(math.pi/2,0,0));T("Iron Tire",(x,y,1),.91,.07,iron,(math.pi/2,0,0));C("Hub",(x,y,1),.23,.32,brass,(math.pi/2,0,0))
  for a in range(8):
   z=a*math.tau/8;B("Spoke",(x+math.cos(z)*.3,y,1+math.sin(z)*.3),(.4,.07,.065),wood,(0,-z,0))
B("Cabin",(.1,0,2.45),(2.9,1.15,.6));B("RearWall",(3,0,3.35),(.12,1.2,1.2))
for x in (-2.6,-1.35,-.1,1.15,2.4):Q("Brass Roof Arch",[(x,-1.35,4.12),(x,-1.12,5.18),(x,0,5.68),(x,1.12,5.18),(x,1.35,4.12)],.115,brass)
for x in (-2,-.7,.6,1.9):B("Roof Layer",(x,0,5.24),(.61,1.42,.1),teal)
B("Ridge",(0,0,5.72),(3.1,.13,.13),brass);C("Chimney",(1.55,.35,6.12),.22,.8,iron);S("Roof Crystal",(-1.3,.2,6),(.25,.25,.55),cyan)
B("Counter",(-.2,-1.82,3.1),(1.55,.62,.12),light,(.18,0,0));B("Awning bar",(-.2,-1.42,4.65),(1.72,.09,.09),brass)
for i in range(5):B("Awning",(-1.55+i*.68,-1.62,4.35),(.29,.48,.07),teal if i%2 else light,(.45,0,0))
B("Door",(2.45,-1.18,3.25),(.43,.08,.84),purple);B("Sign",(-3.15,-.05,4.15),(.13,.82,.55),light);T("Alchemical Glyph",(-3.32,-.78,4.18),.27,.035,brass,(math.pi/2,0,.2))
for i,x in enumerate((-1.15,-.72,-.28,.16,.63,1.05)):
 S("Potion",(x,-2.05,3.46),(.16,.16,.23),cyan if i%2 else pink);C("Potion Neck",(x,-2.05,3.72),.06,.18,light)
for x in (-2.25,1.75):S("Lantern",(x,-1.38,4.32),(.15,.15,.22),cyan);T("Lantern Hoop",(x,-1.38,4.48),.19,.03,brass,(math.pi/2,0,0))
for side in (-1,1):Q("Root Vine",[(-2.8,side*1.28,2.1),(-1.8,side*1.42,1.9),(-.6,side*1.3,2.05),(.6,side*1.36,1.85)],.07,moss)
B("Ground",(0,0,-.12),(7.8,7.8,.12),ground)
w=bpy.data.worlds.new("World");bpy.context.scene.world=w;w.use_nodes=True;w.node_tree.nodes["Background"].inputs["Color"].default_value=(.008,.012,.025,1);w.node_tree.nodes["Background"].inputs["Strength"].default_value=.3
for p,e,c in [((4,-6,8),1200,(1,.42,.16)),((-5,-3,5),900,(.1,.55,1)),((2,5,7),1000,(.42,.15,1))]:
 bpy.ops.object.light_add(type="AREA",location=p);o=bpy.context.object;o.data.energy=e;o.data.color=c;o.data.shape="DISK";o.data.size=5;aim(o,(0,0,3))
bpy.ops.object.camera_add(location=(10,-12,8.2));cam=bpy.context.object;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine="BLENDER_EEVEE";sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.image_settings.file_format="PNG";sc.view_settings.look="AgX - Medium High Contrast"
def render(n,p,t=(0,0,3)):
 cam.location=p;aim(cam,t);sc.render.filepath=os.path.join(R,"Preview","Phase_1",n+".png");bpy.ops.render.render(write_still=True)
render("Hero_ThreeQuarter",(10,-12,8.2));render("Front_Shop",(0,-14,5.5),(0,-.3,3.2));render("Side_Profile",(-11,-.2,5.2))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,"Blender","Wandering_Alchemist_v2_Phase_1_Concept.blend"))
def D(n,t):open(os.path.join(R,"Documentation",n),"w",encoding="utf-8").write(t)
D("PROGRESS.md","# Progress\n\n- [x] Phase 0 project setup; Blender 5.2 verified\n- [x] Phase 0 market research\n- [x] Phase 1 3D concept blockout and three check renders\n- [ ] Awaiting user approval before detailed modelling\n\nDirection: The Amber Moth Apothecary — honey wood, teal canvas, brass roof arches, glowing potion counter, asymmetrical roof crystal/chimney, original alchemical sign.\n")
D("TASKS.md","# Tasks\n\n- [x] New independent project\n- [x] Original 3D Phase 1 silhouette\n- [x] Front / side / hero renders\n- [ ] User approval\n- [ ] Detailed mesh, interior, reusable props, UV/PBR, animation, export QA\n")
D("Market_Research.md","# Market Research — 2026-10-10\n\nReferences informed scope only; no assets/designs copied.\n\n- Fab Fantasy Merchant Wagon Truck — 183,570 triangle stylized FBX listing: premium vehicles need readable cargo/mechanical storytelling.\n- Fab Medieval Merchant Caraval Wagon Low-poly — wooden caravan/canvas/cargo/lantern silhouette: travel function needs clear visual storytelling.\n- Fab Medieval Merchant Cart Detailed Market Wagon — PBR 4K, 48k-tri claim, portable formats: product must disclose technical facts honestly.\n- CGTrader Stylized Wizard Potion Flasks Alchemy Set: distinct vessels should remain reusable props.\n\nSources:\nhttps://www.fab.com/listings/f76d1a20-49ee-4ad9-bccc-5c68e07127d9\nhttps://www.fab.com/listings/7c6fd052-a6fd-4e30-9a64-4423590d995a\nhttps://www.fab.com/listings/934d1ce7-33e3-4c0e-9cce-7bf917cb05ee\nhttps://www.cgtrader.com/3d-models/science/laboratory/stylized-low-poly-wizard-potion-flasks-alchemy-set-3d-asset\nhttps://www.artstation.com/marketplace/p/Jw00W/potions-caravan\n\nNo revenue or sales estimates were inferred.\n")
D("Technical_Specifications_Phase_1.md","# Phase 1 Technical Status\n\nBlender 5.2 / Eevee Next. This is a real geometry concept blockout, not final commercial deliverables. UVs, texture-map PBR, interior, animation, exports and game optimization are intentionally pending approval.\n")

