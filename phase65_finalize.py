# -*- coding: utf-8 -*-
import bpy, os
from mathutils import Vector
root = r'C:\Game\Commercial_3D\Wandering_Alchemist_v2'
s = bpy.data.scenes['Scene']
cam = s.camera
original_location = cam.location.copy()
original_rotation = cam.rotation_euler.copy()
original_scale = cam.data.ortho_scale
original_path = s.render.filepath
cam.location = (-2.8, -5.8, 5.3)
cam.rotation_euler = (Vector((-.9, -.8, 3.6)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.ortho_scale = 3.5
s.render.filepath = os.path.join(root, 'renders', 'closeups', 'canopy_trial.png')
bpy.ops.render.render(write_still=True, scene=s.name)
cam.location = original_location
cam.rotation_euler = original_rotation
cam.data.ortho_scale = original_scale
s.render.filepath = original_path
with open(os.path.join(root, 'reports', 'qa.md'), 'a', encoding='utf-8') as f:
    f.write('\n## Fabric macro correction\n\nInitial repeat=5 and normal strength=0.22 looked overly smooth. The final trial uses repeat=1, normal strength=0.85 and sheen=0.25. The weave is deliberately coarser for stylized visual readability, not calibrated physical scan scale. linen_macro.png was inspected at 1000×800, 96 samples, denoising off. Board and neutral hero were rerendered after the correction. Material sample board uses 64 samples.\n')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root, 'Blender', 'Wandering_Alchemist_Phase6_5_Premium.blend'))
print('Canopy closeup refreshed; QA records exact final fabric settings.')
