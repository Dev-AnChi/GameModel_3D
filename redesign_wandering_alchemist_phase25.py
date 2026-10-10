# -*- coding: utf-8 -*-
import bpy,os,math,shutil
from mathutils import Vector
R=r"C:\Game\GameModel_3D\Wandering_Alchemist_v2";src=os.path.join(R,"Blender","Wandering_Alchemist_v2_Phase_2_DetailMaterials.blend");B=os.path.join(R,"Blender");P=os.path.join(R,"Preview","Phase_2_5_Pass_AB");os.makedirs(P,exist_ok=True);os.makedirs(os.path.join(B,"Backups"),exist_ok=True);shutil.copy2(src,os.path.join(B,"Backups","Wandering_Alchemist_v2_Phase_2_Backup.blend"));bpy.ops.wm.open_mainfile(filepath=src)
def mat(n,c,met=0,rough=.4):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=met;p.inputs["Roughness"].default_value=rough;return m
oak=mat("Premium Warm Oak",(.24,.075,.025),0,.5);edge=mat("Oak Edge",(.48,.17,.045),0,.42);brass=mat("Antique Brass",(.36,.16,.025),.8,.32);iron=mat("Wrought Iron",(.035,.045,.05),.85,.4);ivory=mat("Warm Ivory",(.55,.43,.25),0,.78)
def st(o,m,b=.03):
 o.data.materials.append(m)
 if b:x=o.modifiers.new("Natural Bevel","BEVEL");x.width=b;x.segments=3
 return o
def box(n,p,s,m=oak,r=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(location=p,rotation=r);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return st(o,m)
def cy(n,p,ra,d,m=oak,r=(0,0,0),v=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=ra,depth=d,location=p,rotation=r);o=bpy.context.object;o.name=n;return st(o,m,.025)
def tor(n,p,a,b,m,r=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=a,minor_radius=b,major_segments=32,minor_segments=8,location=p,rotation=r);o=bpy.context.object;o.name=n;return st(o,m)
# Hide the former solid-disk wheel assemblies from render and viewport.
for o in bpy.data.objects:
 if o.name.startswith(("Wheel","Iron_Tire","Hub","Spoke","Axle")):o.hide_render=True;o.hide_viewport=True
# New four spoked wheels: segment rim, iron tyre, deep brass hub, rivets, visible axle.
for x in (-2.75,2.7):
 cy("Rebuilt Axle",(x,0,1.03),.15,3.45,iron,(math.pi/2,0,0))
 for y in (-1.49,1.49):
  tor("Iron Tyre",(x,y,1.03),.91,.075,iron,(math.pi/2,0,0));cy("Deep Brass Hub",(x,y,1.03),.25,.36,brass,(math.pi/2,0,0))
  for a in range(12):
   q=a*math.tau/12;mx=x+math.cos(q)*.79;mz=1.03+math.sin(q)*.79
   box("Segmented Oak Rim",(mx,y,mz),(.16,.13,.10),edge,(0,-q,0))
   if a%2==0:cy("Tyre Rivet",(x+math.cos(q)*.89,y*1.01,1.03+math.sin(q)*.89),.035,.06,brass,(math.pi/2,0,0),10)
  for a in range(10):
   q=a*math.tau/10;box("Tapered Wheel Spoke",(x+math.cos(q)*.36,y,1.03+math.sin(q)*.36),(.43,.065,.07),oak,(0,-q,0))
# Strong frame, plank read, undercarriage crossbeams and mechanical hangers.
for x in (-3.0,-2.2,-1.2,-.2,.8,1.8,2.8):box("Body Plank", (x,-1.29,2.55),(.34,.055,.45),oak)
for x in (-2.95,2.95):
 box("Structural Upright",(x,0,2.65),(.13,1.32,.9),edge);box("Corner Iron Brace",(x,-1.35,2.1),(.18,.04,.12),iron)
for x in (-2.4,0,2.4):box("Chassis Crossbeam",(x,0,1.45),(.10,1.55,.13),iron)
box("Rear Door",(3.12,.0,3.22),(.08,.88,1.0),oak);box("Rear Door Frame",(3.2,0,4.2),(.09,1.05,.08),edge)
for y in (-.62,.62):cy("Rear Hinge",(3.23,y,3.2),.07,.3,iron,(0,math.pi/2,0));box("Rear Brace",(3.25,y,3.3),(.04,.04,.78),brass,(0,.55,0))
box("Rear Step",(3.72,0,1.55),(.42,.75,.10),edge);box("Rear Luggage Rack",(3.42,0,4.55),(.22,1.15,.12),iron)
for y in (-.72,.72):box("Rack Strap",(3.56,y,4.35),(.08,.08,.32),brass)
# rear window, lock, small crate and luggage hooks make reverse side purposeful
box("Rear Window Frame",(3.22,0,3.65),(.045,.35,.30),brass);box("Rear Window",(3.24,0,3.65),(.035,.27,.22),ivory);box("Rear Lock",(3.26,0,2.7),(.06,.12,.12),brass)
box("Tool Crate",(2.75,1.35,2.1),(.55,.28,.32),oak);box("Crate Strap",(2.75,1.63,2.1),(.59,.03,.06),brass)
for y in (-.9,.9):tor("Luggage Hook",(2.7,y,3.85),.12,.025,iron,(math.pi/2,0,0))
# neutral / beauty review.
sc=bpy.context.scene;cam=sc.camera
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def ren(n,p,t=(0,0,3),neutral=False):
 cam.location=p;aim(cam,t);sc.render.resolution_x=1000;sc.render.resolution_y=750;sc.render.filepath=os.path.join(P,n+".png")
 sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.16,.16,.16,1) if neutral else (.008,.012,.025,1);sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.55 if neutral else .28;bpy.ops.render.render(write_still=True)
ren("Beauty_Hero_Front_ThreeQuarter",(10,-12,8.2));ren("Beauty_Rear_ThreeQuarter",(-9,11,7.5));ren("Beauty_Side",(-11,-.2,5.2));ren("Beauty_Wheel_Closeup",(-4,-6,2.8),(-2,-1.4,1.2));ren("Neutral_Hero",(10,-12,8.2),neutral=True);ren("Neutral_Rear",(-9,11,7.5),neutral=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(B,"Wandering_Alchemist_v2_Phase_2_5_Pass_AB.blend"))
open(os.path.join(R,"Documentation","Phase_2_5_Pass_AB_Report.md"),"w",encoding="utf-8").write("# Phase 2.5 — Pass A/B\n\nBackup of Phase 2 made before edits. Replaced visible former solid wheels with 4 physical segmented oak rims, 10 spokes each, deep hubs, iron tyres, rivets and axles. Added structural body planks/crossbeams, rear door/frame/window/lock/hinges, step, luggage rack, straps, hooks and crate. Canopy and potion redesign were intentionally deferred to Pass C/D.\n")

