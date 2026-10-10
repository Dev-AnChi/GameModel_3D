# -*- coding: utf-8 -*-
import bpy, json, math
from pathlib import Path

ROOT = Path('C:/Game/GameModel_3D')
S = bpy.context.scene
NS = bpy.app.driver_namespace
particles = [o for o in S.objects if o.name.startswith('HERO spray particle')]


def capture(frame):
    S.frame_set(frame)
    bpy.context.view_layer.update()
    return {o.name: list(o.location) + list(o.scale) for o in particles}


a, b = capture(1), capture(301)
error = max((abs(x - y) for name in a for x, y in zip(a[name], b[name])), default=0)
shader_rows = []
water_materials = {o.active_material for o in bpy.data.collections['HERO C | Falling water'].objects}
for mat in water_materials:
    images = [n.image.name for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    drivers = mat.node_tree.animation_data.drivers if mat.node_tree.animation_data else []
    shader_rows.append({'material': mat.name, 'images': images,
                        'drivers': [{'expression': f.driver.expression, 'valid': f.driver.is_valid} for f in drivers]})
results = {
    'blend': str(ROOT / 'Catmosphere_Hero_Environment.blend'),
    'frame_range': [S.frame_start, S.frame_end], 'fps': S.render.fps,
    'new_cascades': len(bpy.data.collections['HERO C | Falling water'].objects),
    'intermediate_pools': len([o for o in S.objects if o.name.startswith('HERO pool ') and o.name.removeprefix('HERO pool ').isdigit()]),
    'spray_mesh_particles': len(particles), 'particle_loop_1_301_max_error': error,
    'water_materials': shader_rows,
    'packed_hero_water_images': [{'name': im.name, 'packed': bool(im.packed_file),
                                  'dimensions': list(im.size)} for im in bpy.data.images
                                if im.name in ['doodlebuilt_waterfall_fx.png', 'normal.png']],
    'render_outputs': [{'name': p.name, 'bytes': p.stat().st_size} for p in sorted((ROOT / 'renders').glob('catmosphere_hero_*.png'))],
    'limitations': ['No exhaustive geometry collision test', 'No newly exported full-scene animation video',
                    'Visual premium quality remains unapproved'],
}
S.frame_set(75)
S.camera = bpy.data.objects['HERO | Main portrait camera']
S.render.resolution_x = 1080; S.render.resolution_y = 1920
for n in S.compositing_node_group.nodes:
    if n.bl_idname == 'CompositorNodeScale':
        n.inputs['X'].default_value = 1080 / 941
        n.inputs['Y'].default_value = 1080 / 941
S.render.filepath = str(ROOT / 'renders' / 'catmosphere_hero_final.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Catmosphere_Hero_Environment.blend'))
(ROOT / 'reports' / 'catmosphere_hero_validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(results, ensure_ascii=False))
