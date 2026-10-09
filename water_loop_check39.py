# -*- coding: utf-8 -*-
"""Inspect exact 300-frame prototype phase, plus rendered boundary samples."""
import bpy, json
ROOT='C:/Game/GameModel_3D'
NS=bpy.app.driver_namespace
def check():
    p=bpy.data.scenes['W39 | Prototype Animation Review']
    c=bpy.data.collections['W39 | Pass A Waterfall Prototype']
    old=bpy.context.window.scene;bpy.context.window.scene=p
    def sample(frame):
        p.frame_set(frame);p.view_layers[0].update()
        dg=bpy.context.evaluated_depsgraph_get()
        return {o.name:[v for row in o.evaluated_get(dg).matrix_world for v in row] for o in c.objects}
    a=sample(1);b=sample(301)
    errors={name:max(abs(x-y) for x,y in zip(v,b[name])) for name,v in a.items()}
    invalid=[]
    for o in c.objects:
        if o.animation_data:
            invalid.extend([o.name+' : '+d.data_path for d in o.animation_data.drivers if not d.driver.is_valid])
    data={'prototype_objects':len(c.objects),'max_frame_1_301_matrix_delta':max(errors.values()),
          'invalid_object_drivers':invalid,'collision_candidates':NS.get('w39_final_collision'),
          'status':NS.get('w39_animation_status')}
    with open(ROOT+'/reports/water_loop_validation.json','w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    print(json.dumps(data,ensure_ascii=False))
    p.render.image_settings.media_type='IMAGE';p.render.image_settings.file_format='PNG'
    for frame in [1,301]:
        p.frame_set(frame);p.render.filepath=ROOT+f'/renders/water_loop_{frame:03d}.png'
        bpy.ops.render.render(write_still=True,scene=p.name)
    p.render.image_settings.media_type='VIDEO';p.render.image_settings.file_format='FFMPEG';p.render.filepath=ROOT+'/renders/water_animation_preview.mp4'
    p.frame_set(75);bpy.context.window.scene=old;bpy.data.scenes['Scene'].frame_set(75)
    NS['w39_api']['verify']()
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Catmosphere_Water_Master.blend')
NS['w39_loop_check']=check
