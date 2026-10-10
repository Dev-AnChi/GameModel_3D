# -*- coding: utf-8 -*-
import bpy,os,json
ROOT=r'C:\Game\Commercial_3D\Wandering_Alchemist_v2'
with open(os.path.join(ROOT,'textures','downloaded','verified_manifest.json'),encoding='utf-8') as f:assets=json.load(f)
assign={'oak_veneer_01':('P65A_Oak_Trial','Oak_Test_Plank; Shop_Counter_Plank'),'rough_linen':('P65A_Teal_Linen_Trial','Teal_Linen_Test_Drape; Draped_Canopy_Surface'),'metal_plate_02':('P65A_Antique_Brass_Trial','Antique_Brass_Test; Layered_Hub')}
sources='# Material Sources — Phase 6.5A\n\nPowered by Poly Haven. Download date: 2026-10-10. Asset license verified at https://polyhaven.com/license — CC0 allows commercial use and redistribution in sold products.\n\n'
for a in assets:
    m,objects=assign[a['id']]
    sources+=f"## {a['name']}\n\n- Source: {a['page']}\n- Authors: {', '.join(a['authors'])}\n- License: CC0\n- Used Blender material: {m}\n- Assigned objects: {objects}\n"
    for role,rec in a['files'].items():sources+=f"- {role}: {rec['path']} — {rec['resolution']}, {rec['bytes']} bytes, HTTP {rec['http_status']}, MD5 {rec['md5']}\n"
    sources+='\n'
sources+='Metal Plate 02 is a steel surface, not a downloaded brass scan. Its surface variation/roughness/normal is reused with original brass tint and metallic=1; normal strength is reduced to 0.10. Rough Linen is recolored teal. Oak is tinted warm brown. Glass and liquid are original shaders and geometry, without downloaded glass textures.\n'
audit=[]
for m in bpy.data.materials:
    if not m.name.startswith('P65A_'):continue
    record={'material':m.name,'images':[],'assigned_objects':[o.name for o in bpy.data.objects if hasattr(o.data,'materials') and m in list(o.data.materials)]}
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:
            p=bpy.path.abspath(n.image.filepath);record['images'].append({'file':p,'exists':os.path.isfile(p),'size':list(n.image.size),'color_space':n.image.colorspace_settings.name,'linked':n.outputs['Color'].is_linked})
            n.image.filepath=bpy.path.relpath(p)
    audit.append(record)
with open(os.path.join(ROOT,'reports','material_audit.json'),'w',encoding='utf-8') as f:json.dump(audit,f,ensure_ascii=False,indent=2)
comparison='''# Reference comparison — Phase 6.5A

The current asset remains substantially below the concept in handcrafted detail and set dressing. No objective 80% beauty claim is possible. Treat the requested 80% as the user's visual approval target, not a computed quality metric.

| Area | Current result | Gap to reference |
|---|---|---|
| Silhouette | Long low wooden caravan, spoked wheels, curved teal canopy | Broad proportions accepted; hero density still lower |
| Wood | Existing five wood sets plus one scanned oak trial plank | Carved edges/end grain/contact dirt and joints need work |
| Cloth | Scanned woven linen trial on canopy | Gravity folds, seams, anchors, patches and embroidery still needed |
| Brass | One textured hub trial | Mechanical hardware and controlled patina require fuller treatment |
| Potion | One transparent thick shell with separate liquid/meniscus, cork | Nine other silhouette studies remain opaque; labels/chains/holders missing |
| Lanterns | Existing placeholder lantern silhouettes | Full frame, glass panels, hook/chain and warm light missing |
| Shop/interior | Existing sparse shelves and drawers | Tools, books, scrolls, herbs, containers and full working interior missing |
| Rear | Existing arched plank door | Window, hinges, lock, handle and luggage detail missing |

Only Phase 6.5A performed: resource download, verification, test board and selected component trials. Full integration and detail reconstruction stop here for the user's material review, as the brief requests.
'''
qa='''# QA — Phase 6.5A

- Blender MCP connected; Blender 5.2.2 LTS protocol 13.
- Source: Wandering_Alchemist_Phase6A_Wood.blend.
- Preserved backup: Blender/Backups/Before_Phase6_5_20261010_152531.blend.
- Downloaded nine maps via official public API manifest URLs: HTTP 200, exact file size, MD5 matches, Pillow decoded all images. Oak/metal 2048²; linen 2048×2052 (native source aspect).
- Base color is sRGB; Roughness and OpenGL Normal are Non-Color. Normals routed through Normal Map nodes.
- Dedicated scene PHASE65A_MATERIAL_TEST rendered in Cycles, neutral light.
- Main scene before/after rendered in Cycles with identical camera, white lights, sample count and resolution.
- One glass shell has actual interior wall and bottom thickness; liquid is separate and top surface is closed. Visual inspection required; no full export/manifold audit claimed.
- No whole-asset integration, export, mobile/game-ready or commercial-ready claim.
- High-detail interior, lanterns, embroidery and remaining potion collection are pending later passes.
'''
files={'material_sources.md':sources,'reference_comparison.md':comparison,'qa.md':qa,'material_audit.md':'# Material Audit\n\nSee material_audit.json for exact node image paths, color spaces, assignments, dimensions and existence checks. Nine source images and four material studies are used. Height/AO were not downloaded in this study; normal is not substituted with height. No baking output is claimed.\n'}
for name,content in files.items():
    with open(os.path.join(ROOT,'reports',name),'w',encoding='utf-8') as f:f.write(content)
for name in ('PROGRESS.md','TASKS.md'):
    with open(os.path.join(ROOT,'Documentation',name),'a',encoding='utf-8') as f:f.write('\n\nPhase 6.5A: 3 verified CC0 texture sets, 9 maps, four material studies, four selected component trials, neutral before/after renders. Bulk integration and Phase 6.5B–E pending material review.\n')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Blender','Wandering_Alchemist_Phase6_5_Premium.blend'))
print('Sources, audits, comparison, QA and progress saved.')
