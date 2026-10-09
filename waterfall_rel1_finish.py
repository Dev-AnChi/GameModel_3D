# -*- coding: utf-8 -*-
"""Fix foam-petal pivot discovered in close-up review; preserve construction data."""
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace
for ob in ns['rel_collection'].objects:
    if 'Curved foam petal' not in ob.name:continue
    if ob.get('pivot_corrected'):continue
    center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
    for v in ob.data.vertices:v.co-=center
    ob.location=center;ob['pivot_corrected']=True
print('FOAM_PIVOTS_FIXED')
for mat in ns['rel_mats'][:2]:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    for noise in nodes:
        if noise.bl_idname!='ShaderNodeTexNoise':continue
        noise.noise_dimensions='4D'
        noise.inputs['W'].driver_add('default_value').driver.expression='1.5*cos(2*pi*(frame-1)*5/300)'
        move=noise.inputs['Vector'].links[0].from_node
        move.inputs[1].driver_remove('default_value',1)
        move.inputs[1].driver_add('default_value',1).driver.expression='1.5*sin(2*pi*(frame-1)*5/300)'
    # Source animation contributes actual fine surface relief, not only recoloring.
    density=next(n for n in nodes if n.bl_idname=='ShaderNodeMapRange')
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.025
    links.new(density.inputs['Value'].links[0].from_socket,bump.inputs['Height'])
    normal=next(n for n in nodes if n.bl_idname=='ShaderNodeNormalMap');links.new(normal.outputs[0],bump.inputs['Normal'])
    for p in nodes:
        if p.type=='BSDF_PRINCIPLED':links.new(bump.outputs[0],p.inputs['Normal'])
print('CYCLIC_BREAKUP_AND_SOURCE_RELIEF_ADDED')
