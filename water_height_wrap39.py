# -*- coding: utf-8 -*-
"""Height utility map border normalization; keep licensed raster originals intact."""
import bpy
ROOT='C:/Game/GameModel_3D'
NS=bpy.app.driver_namespace
def apply():
    for m in bpy.data.materials:
        if not m.name.startswith(('W39 | layered','W39 | white')):continue
        n=m.node_tree.nodes;l=m.node_tree.links
        add=next(a for a in n if a.bl_idname=='ShaderNodeVectorMath' and a.operation=='ADD')
        lane=int(m.name.rsplit(' ',1)[-1])
        for d in m.node_tree.animation_data.drivers:d.driver.expression=f'(frame-1)*{[17,23,29][lane]}/300.0+{[0,.29,.57][lane]}'
        uv=n.new('ShaderNodeSeparateXYZ');l.new(add.outputs[0],uv.inputs[0])
        def math_node(op):
            a=n.new('ShaderNodeMath');assert op in [i.identifier for i in a.bl_rna.properties['operation'].enum_items];a.operation=op;return a
        factors=[]
        for axis in ['X','Y']:
            frac=math_node('FRACT');l.new(uv.outputs[axis],frac.inputs[0])
            mul=math_node('MULTIPLY');mul.inputs[1].default_value=3.141592653589793;l.new(frac.outputs[0],mul.inputs[0])
            sine=math_node('SINE');l.new(mul.outputs[0],sine.inputs[0])
            sq=math_node('MULTIPLY');l.new(sine.outputs[0],sq.inputs[0]);l.new(sine.outputs[0],sq.inputs[1]);factors.append(sq)
        weight=math_node('MULTIPLY');l.new(factors[0].outputs[0],weight.inputs[0]);l.new(factors[1].outputs[0],weight.inputs[1])
        for tex in [a for a in n if a.type=='TEX_IMAGE' and a.image and a.image.name=='height.png']:
            consumers=[link.to_socket for link in list(tex.outputs['Color'].links)]
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.label='Measured height seam correction / C1 border'
            mix.inputs[1].default_value=(.4,.4,.4,1);l.new(weight.outputs[0],mix.inputs[0]);l.new(tex.outputs['Color'],mix.inputs[2])
            for socket in consumers:l.new(mix.outputs['Color'],socket)
    print('HEIGHT_WRAP_CORRECTED_AND_LANE_PHASES_OFFSET')
def render():
    NS['w39_seam']['render']()
NS['w39_height']={'apply':apply,'render':render}
