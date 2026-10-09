# -*- coding: utf-8 -*-
"""Controlled per-category rollout, verification and report generation in Blender."""
import bpy
import json
from pathlib import Path
from collections import Counter
from mathutils import Vector

ROOT=Path('C:/Game/GameModel_3D')
NS=bpy.app.driver_namespace
API=NS['m37_api']


def preserved(m):
    name=m.name.lower()
    if name.startswith('environment') or 'cloud depth' in name:return True
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
    return bool(p and p.inputs.get('Emission Strength') and (p.inputs['Emission Strength'].is_linked or p.inputs['Emission Strength'].default_value>0))


def rollout(group):
    scene=NS['m37_source']
    cache=NS.setdefault('m37_rollout_cache',{})
    changes=0
    for o in scene.objects:
        if not hasattr(o.data,'materials') or o.hide_render:continue
        # Linked data is deliberately preserved; slot replacements use OBJECT linking.
        for slot in o.material_slots:
            src=slot.material
            if not src or src.name.startswith('M37 |') or preserved(src):continue
            kind=API['category'](src.name)
            if kind!=group:continue
            axis=0;scale=(1,1,1)
            if kind=='Wood':
                pts=[Vector(c) for c in o.bound_box]
                spans=[max(p[a] for p in pts)-min(p[a] for p in pts) for a in range(3)]
                axis=max(range(3),key=lambda a:spans[a])
                scale=tuple(round(abs(v),5) for v in o.matrix_world.to_scale())
            key=(src.name,kind,axis,scale)
            if key not in cache:
                cache[key]=API['material'](src,kind,axis,scale)
                cache[key]['source_material']=src.name
                cache[key]['metric_scale']=scale
                cache[key]['grain_axis']=axis
                if kind=='Glass':
                    for prop in ['surface_render_method','use_transparency_overlap','use_raytrace_refraction']:
                        if hasattr(src,prop) and hasattr(cache[key],prop):setattr(cache[key],prop,getattr(src,prop))
            slot.link='OBJECT';slot.material=cache[key]
            changes+=1
    NS.setdefault('m37_group_results',[]).append({'category':group,'slots':changes})
    print('ROLLOUT',group,'slots',changes,'new materials total',len(cache))


def compatibility():
    scene=NS['m37_source']
    used=set(slot.material for o in scene.objects for slot in o.material_slots if slot.material)
    for m in used:
        if preserved(m):m['godot_compatibility']='BLENDER_BEAUTY_ONLY'
        elif not m.name.startswith('M37 |'):
            spatial=any(n.type in {'TEX_NOISE','TEX_IMAGE','TEX_WAVE','BUMP','VALTORGB','TEX_VORONOI'} for n in m.node_tree.nodes) if m.use_nodes else False
            m['godot_compatibility']='BAKE_REQUIRED' if spatial else 'DIRECT_GLTF_PRINCIPLED_CONSTANTS'
    return [{'name':m.name,'category':API['category'](m.get('source_material',m.name)),'godot':m.get('godot_compatibility'),'visible_users':sum(any(slot.material==m for slot in o.material_slots) for o in scene.objects if not o.hide_render)} for m in sorted(used,key=lambda m:m.name)]


def verify():
    scene=NS['m37_source']
    now=API['signature'](scene)
    original=NS['m37_signature']
    changed=[name for name,digest in original.items() if now.get(name)!=digest]
    missing=[name for name in original if name not in now]
    images=[]
    for im in bpy.data.images:
        if im.source=='FILE':
            if not im.packed_file:im.pack()
            noncolor=any(t in im.name for t in ['Rough','Displacement','nor_gl'])
            expected='Linear Rec.709' if im.name.startswith('monochrome_studio') else 'Non-Color' if noncolor else 'sRGB'
            images.append({'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'space':im.colorspace_settings.name,'correct_space':im.colorspace_settings.name==expected})
    invalid=[m.name for m in bpy.data.materials if m.name.startswith('M37 |') and not any(n.type=='OUTPUT_MATERIAL' and n.inputs['Surface'].is_linked for n in m.node_tree.nodes)]
    animation_checks=[]
    for key,m in NS.get('m37_rollout_cache',{}).items():
        source=bpy.data.materials[key[0]]
        if source.use_nodes and source.node_tree.animation_data:
            old=[(d.data_path,d.array_index,d.driver.expression) for d in source.node_tree.animation_data.drivers]
            new=[(d.data_path,d.array_index,d.driver.expression) for d in m.node_tree.animation_data.drivers] if m.node_tree.animation_data else []
            animation_checks.append({'source':source.name,'material':m.name,'drivers':new,'preserved':new==old})
    data={'original_objects':len(original),'current_source_objects':len(scene.objects),'geometry_transform_modifier_action_changes':changed,'missing_original_objects':missing,'new_objects':sorted(set(now)-set(original)),
          'images':images,'invalid_shader_outputs':invalid,'material_animation_checks':animation_checks,'engine':scene.render.engine,
          'color_management':{'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma},
          'render_samples':getattr(scene.eevee,'taa_render_samples',None),'compatibility':compatibility(),'groups':NS.get('m37_group_results',[])}
    (ROOT/'reports/material_validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('VALIDATION',{'changed':changed,'missing':missing,'invalid':invalid,'images':len(images),'packed':all(i['packed'] for i in images),'spaces':all(i['correct_space'] for i in images)})
    return data


def reports(validation):
    audit=NS['m37_baseline'];rows=audit['materials']
    text=['# Catmosphere — Material Audit Phase 3.7','',
          'Nguồn: Catmosphere_Organic_Master.blend, được người dùng chọn rõ trong chat. Blender 5.2.2 LTS, Eevee, addon 1.8/protocol 13.',
          'Bản gốc được giữ nguyên; backup live scene: Catmosphere_Organic_PreMaterial_20261009.blend. Bản World Detailed mở lúc đầu được lưu riêng: Catmosphere_PreMaterial_20261009.blend.',
          '',f'Audit nguồn: {len(rows)} material được tham chiếu (bao gồm object cũ đang ẩn), {audit["objects"]} object. {sum(r["constant_color"] for r in rows)} màu hằng, {sum(r["uniform_surface_roughness"] for r in rows)} không có roughness thay đổi trên bề mặt, {sum(r["missing_normal"] for r in rows)} thiếu normal/bump. Wood có roughness khác nhau giữa object nhưng đồng đều trên mỗi object.',
          '', '## Phân loại và lỗi ban đầu','',
          '| Material | Nhóm | Object tham chiếu | Màu hằng | Roughness bề mặt đều | Thiếu normal | Mapping ban đầu |',
          '|---|---|---:|---|---|---|---|']
    for r in rows:
        text.append('| '+r['name'].replace('|','/')+' | '+r['category']+' | '+str(r['objects'])+' | '+str(r['constant_color'])+' | '+str(r['uniform_surface_roughness'])+' | '+str(r['missing_normal'])+' | '+', '.join(r['mapping'])+' |')
    text+=['','## Mapping, repetition và màu sắc','',
           'Generated 0–1 khiến hạt noise/vân không có kích thước vật lý đồng nhất trên mesh lớn/nhỏ. Không có image texture trong nguồn nên không phát hiện tiled bitmap; repetition chủ yếu đến từ generic noise cùng hệ số trên các object/mesh giống nhau. Wood quá đều trên mỗi tấm; rock/cloth nhiều vùng thiếu phản ứng bề mặt. Bronze dùng Metallic 0 trong nguồn nên chưa có phản ứng kim loại.',
           'Material mới dùng Position theo mét cho rock/fabric/ground và box projection cho scan đá. Wood dùng Position chuyển WORLD → OBJECT và bù scale thực theo object, chọn chiều dài bbox làm hướng vân; Object Info Random lệch pha giữa tấm để giảm lặp. Không chỉnh UV, geometry, bố cục hoặc animation gốc. Leaf/petal giữ Generated cho gradient cục bộ nhưng micro-normal dùng mét. Rock phủ scan 2.7 m và thêm noise rộng để giảm repetition; oak roughness 1.2 m.',
           'Palette giữ honey wood, cream-gray limestone, botanical greens, hoa pink/yellow/ivory, sofa cream và bedroom lavender-blue. Water có IOR 1.333, turquoise, normal hai tần số và roughness thấp. Không dùng metallic để tạo nước phản chiếu.',
           '', '## Prototype và đánh giá','',
           'Ba scene độc lập gồm bản sao Organic primary terrace rock_03, nhóm Zone_4_floorboard_08–14 và sofa/phụ kiện. Camera, hai area light trắng, HDRI studio, exposure 0, geometry và resolution 1000 × 750 được giữ nguyên giữa before/after. Có render thật bằng Eevee và kiểm tra ảnh. Camera test được sửa trước khi xuất bộ before/after cuối; ảnh trống trong lần kiểm tra đầu đã được thay bằng render hợp lệ.',
           'Lần 1: đá chưa đủ lớp khoáng, vải có sọc. Lần 2: thêm scan height, lớp strata và fissure nhỏ, moss mềm; giảm độ nổi weave vải, pha irregular fibers. Wood có vân liên tục và roughness theo thớ. Chỉ rollout sau khi xem ba cặp ảnh này. Kiểm tra cận thêm trên cushion (fabric_detail_before/final) rồi hạ tần số weave để sợi đọc rõ hơn mà giảm aliasing; cùng camera và HDRI. Sofa thay đổi có chủ ý nhỏ hơn đá/gỗ để tránh bề mặt thô cứng. Water được chỉnh sáng thêm sau full-scene review vì bản đầu quá tối; beauty renders được cập nhật lại.',
           '', '## Lighting và kiểm thử','',
           'Neutral: ba scene studio trắng và HDRI CC0 Monochrome Studio 03, strength 0.3, exposure 0. Scene M37_Neutral_Map_TextureCheck liên kết geometry/material của bản đồ và dùng bản sao Sun/key/fill màu trắng + HDRI, exposure 0; render overview_material_neutral.png. Beauty: scene Scene giữ rig Organic với Sun chính, soft key/front fill, ánh vàng living và xanh tím bedroom; AgX Medium High Contrast và exposure 0.1. Không tăng exposure để che lỗi bề mặt. Beauty world và background geometry vốn có được giữ.',
           'Render trước/sau toàn scene dùng cùng Camera_LivingRoom, M37_Camera_OrganicCliff, Camera_Rooftop, Camera_Bedroom và Camera_Overview, cùng rig beauty. Các shader mới đã được kiểm tra bằng actual Eevee renders. Rock scan dùng height để tạo normal bump trên box projection; nor_gl đã pack nhưng không cắm tangent-space normal vào box projection để tránh sai hệ tiếp tuyến. Oak chỉ dùng scan roughness; màu/vân wood và cloth micro-normal procedural.',
           'Texture stretching được kiểm bằng metrical mapping và render mẫu/cận; không có UV unwrap hay displacement hình học. Đây là kiểm tra hình ảnh và density theo mét, không phải chứng nhận mọi UV trong scene hoàn hảo. Wood bù scale và chia X/Y/Z; các thanh cong liên tục không có UV dọc đường cong chuyên dụng. Ba Organic flowing water lane giữ nguyên graph Generated và driver chuyển dòng gốc, đồng thời thêm micro-normal theo mét; nhãn material_animation_checks kiểm chứng driver expression/path/index.',
           '', '## Godot / glTF','',
           '| Nhãn | Ý nghĩa |','|---|---|',
           '| DIRECT_GLTF_PRINCIPLED_CONSTANTS | Các material legacy dạng Principled hằng; chỉ các thuộc tính được glTF hỗ trợ. |',
           '| BAKE_REQUIRED | Noise, color ramp, box mapping, bump, moss, vân và cloth cần bake UV textures trước khi giữ chất lượng qua glTF. |',
           '| GODOT_SHADER_REWRITE | Nước có ripple/depth proxy và phản xạ phụ thuộc renderer; cần Godot shader/thiết lập equivalent. |',
           '| BLENDER_BEAUTY_ONLY | Sky, clouds, backdrop và các vật liệu phát sáng được giữ để beauty render; ánh sáng không được xuất như texture. |',
           '', 'Không bake, không xuất GLB mới và không kiểm thử Godot trong Phase 3.7. Không tuyên bố shader procedural xuất trực tiếp hoặc chất lượng tương đương ở Godot. Depth water là gradient nghệ thuật, chưa lấy độ sâu scene thật; không phải fluid simulation.',
           '', '## Validation','',
           f'Object gốc: {validation["original_objects"]}. Object gốc mất: {len(validation["missing_original_objects"])}. Geometry/transform/modifier/action thay đổi: {len(validation["geometry_transform_modifier_action_changes"])}. Camera mới: '+', '.join(validation['new_objects'])+'.',
           f'Texture ảnh pack: {len(validation["images"])}. Shader output lỗi: {len(validation["invalid_shader_outputs"])}. Chi tiết: material_validation.json. Hidden legacy object/material được giữ để khôi phục; không purge.',
           '', '## Material cuối và nhãn tương thích','', '| Material | Nhóm | Object visible | Godot |','|---|---|---:|---|']
    for r in validation['compatibility']:text.append('| '+r['name'].replace('|','/')+' | '+r['category']+' | '+str(r['visible_users'])+' | '+str(r['godot'])+' |')
    (ROOT/'reports/material_audit.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    (ROOT/'reports/material_baseline.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Reports written in UTF-8')


NS['m37_rollout_api']={'rollout':rollout,'verify':verify,'reports':reports}
print('Controlled rollout helpers loaded')
