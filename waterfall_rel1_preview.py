# -*- coding: utf-8 -*-
import bpy, json
from mathutils import Vector
NS=bpy.app.driver_namespace;ROOT='C:/Game/GameModel_3D'
def setup_preview():
    scene=bpy.data.scenes['R39 | Refined Waterfall Animation Review'].copy();scene.name='REL1 | Waterfall animation preview'
    old=bpy.data.collections['R39 | Waterfall_03 Refined']
    if old in list(scene.collection.children):scene.collection.children.unlink(old)
    scene.collection.children.link(NS['rel_collection']);scene.camera=NS['ai_camera']
    scene.frame_start=1;scene.frame_end=300;scene.render.fps=30;scene.render.fps_base=1
    scene.render.resolution_x=464;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=24;scene.render.film_transparent=True
    g=NS['rel_background'].copy();scene.compositing_node_group=g
    for n in g.nodes:
        if n.bl_idname=='CompositorNodeRLayers':n.scene=scene
        if n.bl_idname=='CompositorNodeScale':n.inputs['X'].default_value=464/941;n.inputs['Y'].default_value=464/941
    NS['rel_preview']=scene
    print('REL_PREVIEW',len(scene.objects),scene.name)
def loop_check():
    s=NS['rel_preview'];old=bpy.context.window.scene;bpy.context.window.scene=s
    def snap(frame):
        s.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();state={}
        for o in NS['rel_collection'].objects:
            if o.hide_render:continue
            ev=o.evaluated_get(dg);me=ev.to_mesh();state[o.name]=[tuple(ev.matrix_world@v.co) for v in me.vertices];ev.to_mesh_clear()
        return state
    a=snap(1);b=snap(301);delta=max((Vector(v)-Vector(w)).length for name in a for v,w in zip(a[name],b[name]))
    result={'frame_1_301_geometry_max_delta':delta,'flow_cycles':7,'flow_source_frames':11,'ripple_source_frames':6,'normal_cycles':19,'breakup_cycles':5,'breakup_method':'4D noise with sine/cosine phase, continuous periodic loop'}
    with open(ROOT+'/reports/waterfall_rel1_loop.json','w',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    s.frame_set(75);bpy.context.window.scene=old;print('REL_LOOP',result)
def preview():
    s=NS['rel_preview'];bpy.context.window.scene=s;s.frame_set(1)
    s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.gopsize=30;s.render.filepath=ROOT+'/renders/waterfall_rel1_animation_preview.mp4'
    try:bpy.ops.render.render(animation=True,scene=s.name)
    finally:
        bpy.context.window.scene=NS['ai_scene'];NS['ai_scene'].frame_set(75);NS['ai_scene'].camera=NS['ai_camera'];NS['rel_api']['variant']('new');bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Catmosphere_Water_WaterfallRel1.blend')
    with open(ROOT+'/renders/waterfall_rel1_preview_done.txt','w',encoding='utf-8') as f:f.write('Rendered frames 1–300, 30 FPS.\n')
NS['rel_preview_api']={'setup':setup_preview,'loop':loop_check,'render':preview}
