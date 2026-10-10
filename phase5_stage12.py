# -*- coding: utf-8 -*-
import bpy,os,shutil
from mathutils import Vector
R=r"C:\Game\Commercial_3D\Wandering_Alchemist_v2";B=os.path.join(R,"Blender");S=os.path.join(B,"Wandering_Alchemist_Phase4_Geometry_Master.blend");os.makedirs(os.path.join(R,"renders","reference_comparison"),exist_ok=True);os.makedirs(os.path.join(R,"renders","clay_review"),exist_ok=True);os.makedirs(os.path.join(R,"reports"),exist_ok=True);shutil.copy2(S,os.path.join(B,"Backups","Wandering_Alchemist_Phase4_Backup.blend"));bpy.ops.wm.open_mainfile(filepath=S)
def mat(n,c,r=.5):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes["Principled BSDF"];p.inputs["Base Color"].default_value=(*c,1);p.inputs["Roughness"].default_value=r;return m
teal=mat("Reference Deep Teal Fabric",(.015,.17,.16),.82);ivory=mat("Reference Ivory Trim",(.62,.52,.34),.78);oak=mat("Reference Honey Oak",(.25,.075,.025),.5)
# remove flat roof panels from final visibility
for o in bpy.data.objects:
 if o.name.startswith(("Roof Layer","Awning","Roof_Arch")):o.hide_render=True;o.hide_viewport=True
# continuous curved canopy mesh: sagged cross-section, real thickness via solidify+subsurf
verts=[];faces=[];xs=[-2.85,-1.45,0,1.45,2.85];ys=[-1.42,-.72,0,.72,1.42]
for x in xs:
 for y in ys:
  z=4.65+(.78*(1-(y/1.42)**2))-.12*math.cos(x*2.1) if False else 4.65+(.78*(1-(y/1.42)**2))
  verts.append((x,y,z))
for i in range(4):
 for j in range(4):a=i*5+j;faces.append((a,a+1,a+6,a+5))
me=bpy.data.meshes.new("Continuous Curved Canopy Mesh");me.from_pydata(verts,[],faces);can=bpy.data.objects.new("Continuous Curved Canopy",me);bpy.context.collection.objects.link(can);can.data.materials.append(teal);sol=can.modifiers.new("Canopy Thickness","SOLIDIFY");sol.thickness=.07;sub=can.modifiers.new("Canopy Soft Curvature","SUBSURF");sub.levels=2;sub.render_levels=2
# ivory hem as true curve along each edge
for y in (-1.46,1.46):
 c=bpy.data.curves.new("Canopy Hem","CURVE");c.dimensions="3D";c.bevel_depth=.055;c.bevel_resolution=3;s=c.splines.new("BEZIER");s.bezier_points.add(2)
 for b,p in zip(s.bezier_points,[(-2.9,y,4.63),(0,y,4.73),(2.9,y,4.63)]):b.co=p;b.handle_left_type="AUTO";b.handle_right_type="AUTO"
 o=bpy.data.objects.new("Ivory Canopy Hem",c);bpy.context.collection.objects.link(o);o.data.materials.append(ivory)
# clay screens
sc=bpy.context.scene;cam=sc.camera
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def ren(n,p,t=(0,0,3)):
 cam.location=p;aim(cam,t);sc.render.resolution_x=1000;sc.render.resolution_y=750;sc.render.filepath=n;bpy.ops.render.render(write_still=True)
ren(os.path.join(R,"renders","reference_comparison","Stage2_Front.png"),(0,-14,5.5),(0,0,3.2));ren(os.path.join(R,"renders","reference_comparison","Stage2_Side.png"),(-11,0,5.2));ren(os.path.join(R,"renders","reference_comparison","Stage2_Rear.png"),(-9,11,7.5))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(B,"Wandering_Alchemist_Reference_Master.blend"))
open(os.path.join(R,"REFERENCE_BREAKDOWN.md"),"w",encoding="utf-8").write("""# Reference Breakdown — Stage 1
| Reference feature | Current scene state | Decision |
|---|---|---|
| Warm handcrafted wagon silhouette | Existing spoked wheels/chassis and curved body panels | Keep and refine in later mechanics pass |
| Large teal fabric canopy | Former segmented flat roof panels | Replace with continuous curved, thick canopy mesh and ivory hems |
| Arched rear / shop mass | Curved rear-frame geometry exists | Keep; expand door/window detail later |
| Dense potion retail display | Prototype props exist | Rebuild only in Stage 4 |
| Warm brass lantern language | Existing lantern concepts | Re-art-direct after silhouette approval |
Reference informs overall visual direction only; no geometry or textures were copied.
""")

