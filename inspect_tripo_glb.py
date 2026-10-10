# -*- coding: utf-8 -*-
import bpy, json, math, os
from mathutils import Vector
src = r'C:\Game\GameModel_3D\Wandering_Alchemist_v2\References\Models\tripo_pbr_model_14d23857-8311-470b-a053-77f7083d4962.glb'
out = r'C:\Game\GameModel_3D\tripo_inspection'
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
lo = Vector(tuple(min(v[i] for v in points) for i in range(3)))
hi = Vector(tuple(max(v[i] for v in points) for i in range(3)))
center = (lo + hi) / 2
size = max(hi - lo)
print('GLB_AUDIT', json.dumps({'bounds': [list(lo), list(hi)], 'meshes': [{'name':o.name, 'verts':len(o.data.vertices), 'polygons':len(o.data.polygons), 'uv_layers':len(o.data.uv_layers)} for o in meshes], 'materials':[{'name':m.name,'nodes':[n.type for n in m.node_tree.nodes]} for m in bpy.data.materials if m.use_nodes], 'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images]}, ensure_ascii=False))
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.samples = 32
s.cycles.use_denoising = True
s.render.resolution_x = 1100
s.render.resolution_y = 900
s.render.resolution_percentage = 100
s.world = bpy.data.worlds.new('InspectionWorld')
s.world.use_nodes = True
bg = next(n for n in s.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (.18, .18, .18, 1)
bg.inputs['Strength'].default_value = .6
for name, pos, power, scale in [('Key',(-1,-2,3),700,2),('Fill',(2,1,2),500,2),('Rim',(-2,2,3),900,1.5)]:
    d = bpy.data.lights.new(name,'AREA')
    d.energy = power * size * size / 16
    d.shape = 'DISK'
    d.size = size * scale / 3
    o = bpy.data.objects.new(name,d)
    s.collection.objects.link(o)
    o.location = center + Vector(pos)*size
    o.rotation_euler = (center-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('InspectionCamera');cam=bpy.data.objects.new('InspectionCamera',d);s.collection.objects.link(cam);s.camera=cam
d.type='ORTHO';d.ortho_scale=size*1.25
for name, direction in [('hero',(-1.6,-2.2,1.25)),('reverse',(1.6,2.2,1.25))]:
    cam.location=center+Vector(direction)*size
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=os.path.join(out,name+'.png')
    bpy.ops.render.render(write_still=True)
print('INSPECTION_DONE',out)
