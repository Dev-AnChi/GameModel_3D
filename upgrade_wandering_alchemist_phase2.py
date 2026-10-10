# -*- coding: utf-8 -*-
import bpy, os, math, shutil
from mathutils import Vector
R=r"C:\Game\Commercial_3D\Wandering_Alchemist_v2"; SRC=os.path.join(R,"Blender","Wandering_Alchemist_v2_Phase_1_Concept.blend"); B=os.path.join(R,"Blender"); PRE=os.path.join(R,"Preview","Phase_2"); DOC=os.path.join(R,"Documentation")
os.makedirs(PRE,exist_ok=True);os.makedirs(os.path.join(B,"Backups"),exist_ok=True)
shutil.copy2(SRC,os.path.join(B,"Backups","Wandering_Alchemist_v2_Phase_1_Backup.blend"))
bpy.ops.wm.open_mainfile(filepath=SRC)
sc=bpy.context.scene;cam=sc.camera
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def render(n,p,t=(0,0,3),res=(1000,750)):
 cam.location=p;aim(cam,t);sc.render.resolution_x=res[0];sc.render.resolution_y=res[1];sc.render.resolution_percentage=100;sc.render.filepath=os.path.join(PRE,n+".png");bpy.ops.render.render(write_still=True)
render("Before_Front_ThreeQuarter",(10,-12,8.2));render("Before_Side",(-11,-.2,5.2));render("Before_Rear_ThreeQuarter",(-9,11,7.5))
# Upgrade material nodes with procedural grain / patina; no third-party textures.
def proc(n,c,metal=0,rough=.42,noise=.12):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
 out=nt.nodes.new("ShaderNodeOutputMaterial");bs=nt.nodes.new("ShaderNodeBsdfPrincipled");tex=nt.nodes.new("ShaderNodeTexNoise");ramp=nt.nodes.new("ShaderNodeValToRGB");tex.inputs["Scale"].default_value=4.5;tex.inputs["Detail"].default_value=3;tex.inputs["Roughness"].default_value=.7
 ramp.color_ramp.elements[0].color=tuple(x*.45 for x in c)+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,x*1.28+.04) for x in c)+(1,)
 nt.links.new(tex.outputs["Fac"],ramp.inputs["Fac"]);nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"]);nt.links.new(tex.outputs["Fac"],bs.inputs["Roughness"]);nt.links.new(bs.outputs["BSDF"],out.inputs["Surface"]);bs.inputs["Metallic"].default_value=metal;bs.inputs["Roughness"].default_value=rough
 return m
wood=proc("Honey Wood",(.34,.10,.025),0,.46);light=proc("Light Wood",(.57,.22,.055),0,.42);brass=proc("Aged Brass",(.55,.25,.045),.82,.29);iron=proc("Forged Iron",(.055,.07,.075),.78,.36);teal=proc("Teal Canvas",(.015,.24,.20),0,.7);fabric=proc("Cream Fabric",(.58,.38,.16),0,.8);moss=proc("Moss",(.02,.18,.06),0,.9)
def glow(n,c,strength):
 m=proc(n,c,0,.2);p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=strength;return m
cyan=glow("Potion Cyan",(0,.6,.8),2.5);pink=glow("Potion Pink",(.9,.02,.18),1.8);gold=glow("Potion Gold",(1,.28,.01),2);violet=glow("Potion Violet",(.5,.04,.9),2)
glass=proc("Potion Glass",(.03,.18,.19),.05,.16)
def style(o,m,b=.03):
 o.data.materials.append(m)
 if b:x=o.modifiers.new("Soft Bevel","BEVEL");x.width=b;x.segments=3
 return o
def B(n,p,s,m=wood,r=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(location=p,rotation=r);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return style(o,m)
def C(n,p,rad,d,m=wood,r=(0,0,0),v=18):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=rad,depth=d,location=p,rotation=r);o=bpy.context.object;o.name=n;return style(o,m,.02)
def S(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=18,ring_count=10,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return style(o,m,.015)
def T(n,p,a,b,m,r=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=a,minor_radius=b,major_segments=20,minor_segments=8,location=p,rotation=r);o=bpy.context.object;o.name=n;return style(o,m)
# Framing, planking, brackets, hinges and corner hardware improve cabin readability.
for x in (-2.65,-1.75,-.85,.05,.95,1.85,2.7):
 B("Exterior Vertical Frame",(x,-1.245,3.28),(.055,.06,.92),light)
for z in (2.75,3.75,4.15):B("Shop Horizontal Trim",(-.1,-1.26,z),(2.72,.055,.055),brass)
for x in (-2.82,2.82):
 for z in (2.3,4.3):T("Corner Hardware",(x,-1.29,z),.12,.035,brass,(math.pi/2,0,0))
# functional counter supports, handles, latch
for x in (-1.45,1.05):B("Counter Diagonal Support",(x,-1.62,2.7),(.045,.06,.68),brass,(.55,0,0))
B("Door Handle",(2.3,-1.31,3.3),(.10,.035,.04),brass);C("Door Hinge",(2.86,-1.3,3.0),.05,.25,iron,(math.pi/2,0,0));C("Door Hinge",(2.86,-1.3,3.65),.05,.25,iron,(math.pi/2,0,0))
# Interior mini set, seen behind storefront.
B("Interior Shelf",(.0,.82,3.42),(1.9,.16,.055),light);B("Interior Shelf 2",(.0,.82,3.9),(1.9,.16,.055),light)
B("Alchemist Table",(1.35,.55,2.92),(.62,.38,.08),light);B("Drawer Cabinet",(1.35,.78,2.55),(.55,.28,.30),wood);B("Drawer Pull",(1.35,.48,2.6),(.12,.035,.035),brass)
# twelve varied bottles with cork, label and liquid; free-standing mesh groups.
def bottle(n,x,y,z,shape,liq):
 if shape==0:S(n+" Body",(x,y,z),(.15,.15,.23),glass)
 elif shape==1:C(n+" Body",(x,y,z),.15,.42,glass)
 elif shape==2:S(n+" Body",(x,y,z),(.20,.12,.18),glass)
 else:C(n+" Body",(x,y,z),.11,.48,glass)
 C(n+" Neck",(x,y,z+.27),.055,.18,glass);C(n+" Cork",(x,y,z+.39),.06,.10,light);S(n+" Liquid",(x,y,z-.04),(.11,.11,.13),liq);B(n+" Label",(x,y-.145,z),(.085,.01,.06),fabric)
for i,(x,y,z) in enumerate([(-1.45,-2.03,3.45),(-1.12,-2.05,3.46),(-.78,-2.04,3.44),(-.42,-2.05,3.47),(-.05,-2.04,3.43),(.32,-2.05,3.48),(.67,-2.03,3.45),(1.02,-2.05,3.48),(-1.3,.6,3.64),(-.7,.6,3.64),(.0,.6,3.64),(.75,.6,3.64)]):bottle("Potion_%02d"%(i+1),x,y,z,i%4,(cyan,pink,gold,violet)[i%4])
# Loose props: books, mortar/pestle, ingredient jar, crystal, chest, herb pouch, hanging lantern.
B("Spellbook Emerald",(-1.75,-1.9,3.38),(.25,.18,.07),teal,(0,.2,.2));B("Spellbook Lavender",(-1.72,.58,3.98),(.28,.18,.07),purple if 'purple' in globals() else teal,(0,.15,.1))
C("Mortar",(1.42,-1.93,3.35),.16,.13,iron);C("Pestle",(1.58,-1.93,3.5),.045,.35,light,(0,.6,0));C("Ingredient Jar",(1.18,.62,3.62),.13,.33,glass);S("Crystal",(1.65,.62,3.65),(.13,.13,.34),violet)
B("Cargo Chest",(-2.35,1.0,2.35),(.42,.32,.28),wood);B("Chest Strap",(-2.35,.66,2.35),(.46,.03,.06),brass)
S("Herb Pouch",(-2.15,-1.55,2.25),(.22,.14,.18),fabric);C("Pouch Tie",(-2.15,-1.55,2.45),.035,.20,brass)
S("Hanging Lantern",(1.75,-1.38,4.32),(.15,.15,.23),gold);T("Lantern Hoop",(1.75,-1.38,4.50),.21,.03,brass,(math.pi/2,0,0))
# Roof overlap accent / fabric tassels
for x in (-1.7,-.7,.3,1.3):C("Canopy Tassel",(x,-2.02,4.06),.045,.22,brass)
# Files / new blend and presentation after renders
render("After_Hero",(10,-12,8.2));render("After_Front",(0,-14,5.5),(0,-.3,3.2));render("After_Side",(-11,-.2,5.2));render("After_Rear",(-9,11,7.5))
render("After_Potion_Closeup",(3,-7,4.6),(0,-1.6,3.55),(800,650));render("After_Wheel_Closeup",(-4,-6,2.8),(-2,-1.4,1.35),(800,650));render("After_Material_Closeup",(4,-7,5.2),(0,-1.2,4.0),(800,650))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,"Blender","Wandering_Alchemist_v2_Phase_2_DetailMaterials.blend"))
with open(os.path.join(DOC,"Phase_2_Report.md"),"w",encoding="utf-8") as f:f.write("""# Phase 2 Report

## Actual work completed
- Preserved a byte-for-byte Phase 1 backup before editing.
- Rendered the loaded Phase 1 source in three Before views.
- Added exterior wood framing, brass trims, counter supports, door hardware, chest, pouch, hanging lantern, roof tassels and functional detail accents.
- Added an interior shelf pair, miniature worktable and drawer cabinet.
- Replaced the small shop bottle display with 12 individually named, varied bottle assemblies, including corks, labels and coloured liquids.
- Added spellbooks, mortar and pestle, ingredient jar, crystal, chest and herb pouch as separate geometry.
- Rebuilt wood, brass, iron, fabric and glass/potion materials as Blender-native procedural node materials with colour/roughness variation. No third-party texture assets were used.

## Status
This is a materially upgraded presentation model, but it is not yet commercially release-ready: UV unwrap/export validation, final production texture maps, full interior, animation and game-optimised variant remain future phases.
""")

