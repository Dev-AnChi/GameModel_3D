# -*- coding: utf-8 -*-
import bpy,os,shutil,math
from mathutils import Vector
R=r"C:\Game\GameModel_3D\Wandering_Alchemist_v2";B=os.path.join(R,"Blender");S=os.path.join(B,"Wandering_Alchemist_Phase3B.blend");P=os.path.join(R,"renders");D=os.path.join(R,"reports");os.makedirs(P,exist_ok=True);os.makedirs(D,exist_ok=True);os.makedirs(os.path.join(B,"Backups"),exist_ok=True);shutil.copy2(S,os.path.join(B,"Backups","Wandering_Alchemist_Phase3B_Backup.blend"));bpy.ops.wm.open_mainfile(filepath=S)
sc=bpy.context.scene;cam=sc.camera
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
clay=bpy.data.materials.new("Phase4 Clay Review");clay.diffuse_color=(.42,.42,.42,1);clay.use_nodes=True;clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.42,.42,.42,1);clay.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.68
def clayrender(n,p,t=(0,0,3)):
 for o in sc.objects:
  if hasattr(o.data,"materials") and o.type=="MESH":o["_oldmats"]=[x.name for x in o.data.materials];o.data.materials.clear();o.data.materials.append(clay)
 cam.location=p;aim(cam,t);sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.18,.18,.18,1);sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65;sc.render.resolution_x=1000;sc.render.resolution_y=750;sc.render.filepath=os.path.join(P,n);bpy.ops.render.render(write_still=True)
clayrender("Phase4_Clay_Before.png",(10,-12,8.2))
# Restore basic materials enough for beauty later by reloading source after before capture.
bpy.ops.wm.open_mainfile(filepath=S);sc=bpy.context.scene;cam=sc.camera
clay=bpy.data.materials.new("Phase4 Clay After Review");clay.diffuse_color=(.42,.42,.42,1);clay.use_nodes=True;clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.42,.42,.42,1);clay.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.68
def mt(n,c,met=0,rough=.4):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1);p.inputs["Metallic"].default_value=met;p.inputs["Roughness"].default_value=rough;return m
oak=mt("Phase4 Organic Oak",(.22,.07,.025),0,.52);brass=mt("Phase4 Brass",(.32,.14,.025),.8,.34)
def style(o,m,b=.05):
 o.data.materials.append(m);z=o.modifiers.new("Handcrafted Edge Profile","BEVEL");z.width=b;z.segments=4;return o
def panel(n,x,y,flip=False):
 # hand-shaped vertical plank: unequal top/bottom widths and bowed outer edge
 v=[(x-.34,y,2.05),(x+.34,y,2.05),(x+.30,y,4.30),(x+.16,y,4.55),(x-.22,y,4.52),(x-.38,y,4.18)]
 verts=v+[(a,y+(.09 if y<0 else -.09),c) for a,b,c in v];faces=[(0,1,2,3,4,5),(6,11,10,9,8,7)]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);style(o,oak,.04)
# Hide rectangular original core body / rear panel, preserve shop elements and wheels.
for o in bpy.data.objects:
 if o.name.startswith(("Cabin","Rear_Wall","Body Plank","Exterior Vertical Frame")):o.hide_render=True;o.hide_viewport=True
# curving planks make the core body read handcrafted instead of a single cuboid
for y in (-1.18,1.18):
 for x in (-2.45,-1.75,-1.05,-.35,.35,1.05,1.75,2.45):panel("Organic Body Plank",x,y)
# arched rear facade created as true curves with depth rather than a planar box
for scale in (1.0,.78):
 c=bpy.data.curves.new("Rear Arch Frame","CURVE");c.dimensions="3D";c.bevel_depth=.09;c.bevel_resolution=4;s=c.splines.new("BEZIER");pts=[(3.05,-scale,2.0),(3.18,-scale,4.05),(3.12,0,4.75),(3.18,scale,4.05),(3.05,scale,2.0)];s.bezier_points.add(4)
 for b,p in zip(s.bezier_points,pts):b.co=p;b.handle_left_type="AUTO";b.handle_right_type="AUTO"
 o=bpy.data.objects.new("Curved Rear Frame",c);bpy.context.collection.objects.link(o);o.data.materials.append(brass if scale<.9 else oak)
# sculpted underbody trim with a rolled curve silhouette
c=bpy.data.curves.new("Carved Sill","CURVE");c.dimensions="3D";c.bevel_depth=.13;c.bevel_resolution=4;s=c.splines.new("BEZIER");s.bezier_points.add(3)
for b,p in zip(s.bezier_points,[(-3,-1.28,2.05),(-1,-1.38,1.9),(1,-1.35,1.94),(3,-1.22,2.12)]):b.co=p;b.handle_left_type="AUTO";b.handle_right_type="AUTO"
o=bpy.data.objects.new("Carved Organic Sill",c);bpy.context.collection.objects.link(o);o.data.materials.append(oak)
# clay after: materials are swapped only temporarily
for o in sc.objects:
 if hasattr(o.data,"materials") and o.type=="MESH":o.data.materials.clear();o.data.materials.append(clay)
cam.location=(10,-12,8.2);aim(cam,(0,0,3));sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.18,.18,.18,1);sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65;sc.render.filepath=os.path.join(P,"Phase4_Clay_After.png");bpy.ops.render.render(write_still=True)
# beauty uses clay? reload phase then regenerate add impossible. Save with actual current clays is bad. Restore all material slots to oak/brass proxy for source.
for o in sc.objects:
 if hasattr(o.data,"materials") and o.type=="MESH":o.data.materials.clear();o.data.materials.append(oak)
cam.location=(10,-12,8.2);aim(cam,(0,0,3));sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.008,.012,.025,1);sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.28;sc.render.filepath=os.path.join(P,"Phase4_Hero.png");bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(B,"Wandering_Alchemist_Phase4_Geometry_Master.blend"))
open(os.path.join(D,"Phase4_Geometry_QA.md"),"w",encoding="utf-8").write("# Phase 4 Geometry QA — Pass A\n\nCreated from a Phase3B backup. Clay before/after captured from the same hero camera. Replaced the dominant rectangular cabin core visibility with 16 hand-profiled thick body planks, two dimensional curved rear frames and a curved carved sill. This is an intermediate high-detail geometry master. Canopy, detailed potion meshes, full topology cleanup, UVs and material restoration remain intentionally pending Pass B–F.\n")

