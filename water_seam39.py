# -*- coding: utf-8 -*-
"""Blend a licensed non-seamless waterfall photograph into a tileable utility map."""
import bpy
ROOT='C:/Game/GameModel_3D'
NS=bpy.app.driver_namespace
def apply():
    height=bpy.data.images.get('height.png')
    for m in bpy.data.materials:
        if not m.name.startswith('W39 | white'):continue
        n=m.node_tree.nodes;l=m.node_tree.links
        add=next(a for a in n if a.bl_idname=='ShaderNodeVectorMath' and a.operation=='ADD')
        photo=next(a for a in n if a.type=='TEX_IMAGE' and a.image and 'oga_waterfall' in a.image.filepath)
        mapping=next(a for a in n if a.type=='MAP_RANGE')
        uv=n.new('ShaderNodeSeparateXYZ');uv.location=(-520,600);l.new(add.outputs[0],uv.inputs[0])
        def math_node(op):
            a=n.new('ShaderNodeMath')
            assert op in [i.identifier for i in a.bl_rna.properties['operation'].enum_items]
            a.operation=op;return a
        factors=[]
        for axis in ['X','Y']:
            frac=math_node('FRACT');l.new(uv.outputs[axis],frac.inputs[0])
            mul=math_node('MULTIPLY');mul.inputs[1].default_value=3.141592653589793;l.new(frac.outputs[0],mul.inputs[0])
            sine=math_node('SINE');l.new(mul.outputs[0],sine.inputs[0])
            squared=math_node('MULTIPLY');l.new(sine.outputs[0],squared.inputs[0]);l.new(sine.outputs[0],squared.inputs[1]);factors.append(squared)
        weight=math_node('MULTIPLY');l.new(factors[0].outputs[0],weight.inputs[0]);l.new(factors[1].outputs[0],weight.inputs[1])
        tile=n.new('ShaderNodeTexImage');tile.image=height;tile.extension='REPEAT';tile.label='CC0 seamless fallback across photograph borders';l.new(add.outputs[0],tile.inputs['Vector'])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.label='C1-continuous photograph tile border blend'
        l.new(weight.outputs[0],mix.inputs[0]);l.new(tile.outputs['Color'],mix.inputs[1]);l.new(photo.outputs['Color'],mix.inputs[2]);l.new(mix.outputs['Color'],mapping.inputs['Value'])
    print('PHOTOGRAPH_SEAM_BLEND_APPLIED')
def render():
    s=bpy.data.scenes['Scene'];p=bpy.data.scenes['W39 | Prototype Animation Review']
    s.frame_set(75);bpy.context.window.scene=s;NS['w39_api']['render_after']()
    bpy.context.window.scene=p;p.frame_set(1);p.view_layers[0].update()
    # Warm up the same scene/depsgraph and render configuration used for the clip.
    p.render.image_settings.media_type='IMAGE';p.render.image_settings.file_format='PNG';p.render.filepath=ROOT+'/renders/water_animation_warmup.png'
    bpy.ops.render.render(write_still=True,scene=p.name)
    p.render.image_settings.media_type='VIDEO';p.render.image_settings.file_format='FFMPEG';p.render.filepath=ROOT+'/renders/water_animation_preview.mp4'
    NS['w39_animation_status']='rendering seamless photograph blend'
    bpy.ops.render.render(animation=True,scene=p.name)
    NS['w39_animation_status']='done seamless photograph blend'
    bpy.context.window.scene=s;s.frame_set(75);NS['w39_loop_check']()
NS['w39_seam']={'apply':apply,'render':render}
