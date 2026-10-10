# -*- coding: utf-8 -*-
import bpy,os,shutil,math
from mathutils import Vector
R=r"C:\Game\Commercial_3D\Wandering_Alchemist_v2";B=os.path.join(R,"Blender");S=os.path.join(B,"Wandering_Alchemist_v2_Phase_2_5_Pass_AB.blend");P=os.path.join(R,"Preview","Phase_3_AB");os.makedirs(P,exist_ok=True);os.makedirs(os.path.join(B,"Backups"),exist_ok=True);shutil.copy2(S,os.path.join(B,"Backups","Wandering_Alchemist_v2_Phase_2_5_Backup.blend"));bpy.ops.wm.open_mainfile(filepath=S)
sc=bpy.context.scene;cam=sc.camera
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def ren(n,p,t=(0,0,3)):
 cam.location=p;aim(cam,t);sc.render.resolution_x=1000;sc.render.resolution_y=750;sc.render.filepath=os.path.join(P,n+".png");bpy.ops.render.render(write_still=True)
ren("Before_Phase3_Hero",(10,-12,8.2));ren("Before_Phase3_Rear",(-9,11,7.5))
def m(n,c,me=0,ro=.4):
 x=bpy.data.materials.get(n) or bpy.data.materials.new(n);x.use_nodes=True;p=x.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=me;p.inputs["Roughness"].default_value=ro;return x
oak=m("Phase3 Warm Oak",(.22,.075,.025),0,.53);iron=m("Phase3 Wrought Iron",(.028,.035,.04),.85,.43);brass=m("Phase3 Antique Brass",(.30,.13,.02),.82,.35)
def st(o,a,b=.03):
 o.data.materials.append(a)
 if b:z=o.modifiers.new("Edge Bevel","BEVEL");z.width=b;z.segments=3
 return o
def box(n,p,s,a=oak,r=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(location=p,rotation=r);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return st(o,a)
def cy(n,p,q,d,a=oak,r=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=q,depth=d,location=p,rotation=r);o=bpy.context.object;o.name=n;return st(o,a,.02)
# Pass A: a connected towing assembly, axle saddle brackets, and extra wheel hub collars.
box("Towing Pole",(-5.0,0,1.55),(2.0,.16,.16),oak);box("Tow Yoke",(-6.85,0,1.55),(.18,1.05,.13),oak);cy("Tow Ring",(-7.1,0,1.55),.20,.08,iron,(0,math.pi/2,0))
for x in (-2.75,2.7):
 for y in (-1.05,1.05):box("Axle Saddle",(x,y,1.38),(.24,.18,.13),iron)
 for y in (-1.49,1.49):cy("Hub Collar",(x,y*1.11,1.03),.30,.07,brass,(math.pi/2,0,0))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(B,"Wandering_Alchemist_Phase3A.blend"))
# Pass B: hand-crafted rear façade, cargo and window shutters.
box("Rear Door Crossbrace",(3.30,0,3.22),(.045,.83,.06),brass,(0,.65,0));box("Rear Door Crossbrace",(3.31,0,3.22),(.045,.83,.06),brass,(0,-.65,0))
for y in (-.42,.42):box("Rear Shutter",(3.29,y,3.68),(.045,.18,.28),oak)
box("Rear Lantern Mount",(3.42,-1.0,3.95),(.15,.05,.15),iron);cy("Rear Lantern",(3.5,-1.0,3.72),.13,.32,brass)
box("Side Step",(0,-1.65,1.55),(.85,.35,.10),oak);box("Side Step Support",(0,-1.38,1.3),(.55,.05,.09),iron)
# normals / non-manifold audit is intentionally reported as limited by unapplied modifiers.
ren("After_Phase3_Hero",(10,-12,8.2));ren("After_Phase3_Rear",(-9,11,7.5));ren("After_Phase3_Wheel",(-4,-6,2.8),(-2,-1.4,1.2))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(B,"Wandering_Alchemist_Phase3B.blend"))
open(os.path.join(R,"Documentation","Phase_3_AB_Report.md"),"w",encoding="utf-8").write("# Phase 3 A–B Report\n\nCreated independent backups and checkpoints. Phase3A adds a mechanically connected towing pole/yoke/ring, axle saddles and hub collars to the rebuilt spoked wheel system. Phase3B adds rear door crossbraces, shutters, lantern mount/lantern and a supported side step. Before/after and wheel/rear renders were generated. Pass C–F have not been performed. No game-ready or commercial-ready claim is made; topology/UV/non-manifold/export QA remain pending.\n")

