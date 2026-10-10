# -*- coding: utf-8 -*-
import bpy, os, json
from pathlib import Path
root = Path(r'C:\Game\GameModel_3D')
old = 'C:\\Game\\Commercial_3D'
new = 'C:\\Game\\GameModel_3D'
records = []
for project in ('Wandering_Alchemist', 'Wandering_Alchemist_v2'):
    for path in sorted((root / project / 'Blender').glob('*.blend')):
        bpy.ops.wm.open_mainfile(filepath=str(path))
        changed = []
        missing = []
        for image in bpy.data.images:
            if image.source != 'FILE' or not image.filepath:
                continue
            absolute = bpy.path.abspath(image.filepath)
            fixed = absolute.replace(old, new, 1) if absolute.startswith(old) else absolute
            if fixed != absolute:
                image.filepath = bpy.path.relpath(fixed)
                changed.append(image.name)
            if not image.packed_file and not os.path.isfile(fixed):
                missing.append(fixed)
        for scene in bpy.data.scenes:
            if scene.render.filepath.startswith(old):
                scene.render.filepath = scene.render.filepath.replace(old, new, 1)
                changed.append('render:' + scene.name)
        if changed:
            bpy.context.preferences.filepaths.save_version = 0
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
        records.append({'file': str(path), 'updated_paths': changed, 'missing_images': missing})
        print('PATH_AUDIT', path.name, 'updated', len(changed), 'missing', len(missing))
with open(root / 'wandering_relocation_path_audit.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
print('PATH_RELOCATION_DONE; historical .blend1 and Backups files preserved unchanged')
