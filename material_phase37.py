# -*- coding: utf-8 -*-
"""Phase 3.7: executed in live Blender through Blender MCP, UTF-8 source."""
import bpy
import json
import hashlib
import os
import math
from collections import Counter
from mathutils import Vector

ROOT = 'C:/Game/GameModel_3D'
NS = bpy.app.driver_namespace


def enum(node, prop, value):
    identifiers = [item.identifier for item in node.bl_rna.properties[prop].enum_items]
    if identifiers and value not in identifiers:
        raise ValueError((prop, value, identifiers))
    setattr(node, prop, value)


def category(name):
    name = name.lower()
    if name.startswith('environment'): return 'Decorative materials'
    if 'wood' in name or 'bark' in name: return 'Wood'
    if 'stone' in name or 'rock' in name: return 'Rock'
    if any(t in name for t in ['ground', 'sand', 'soil']): return 'Ground'
    if any(t in name for t in ['fabric', 'linen', 'rope', 'embroidery']): return 'Fabric'
    if any(t in name for t in ['leaf', 'botanical', 'foliage']): return 'Leaves'
    if any(t in name for t in ['flower', 'blossom']): return 'Flowers'
    if 'glass' in name: return 'Glass'
    if 'water' in name: return 'Water'
    if any(t in name for t in ['bronze', 'metal']): return 'Metal'
    return 'Decorative materials'


def signature(scene):
    result = {}
    for o in scene.objects:
        h = hashlib.sha256()
        h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode('utf-8'))
        if o.type == 'MESH':
            h.update(str([(tuple(v.co)) for v in o.data.vertices]).encode('utf-8'))
            h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode('utf-8'))
        h.update(str([(m.name, m.type) for m in o.modifiers]).encode('utf-8'))
        h.update(str(o.animation_data.action.name if o.animation_data and o.animation_data.action else None).encode('utf-8'))
        result[o.name] = h.hexdigest()
    return result


def audit(scene):
    used = set(m for o in scene.objects if hasattr(o.data, 'materials') for m in o.data.materials if m)
    rows = []
    for m in sorted(used, key=lambda m: m.name):
        p = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.use_nodes else None
        spatial_roughness = False
        if p and p.inputs['Roughness'].is_linked:
            visited = set()
            def walk(n):
                if n in visited: return False
                visited.add(n)
                return n.type in {'TEX_NOISE', 'TEX_IMAGE', 'TEX_WAVE', 'TEX_VORONOI'} or any(walk(l.from_node) for i in n.inputs for l in i.links)
            spatial_roughness = any(walk(l.from_node) for l in p.inputs['Roughness'].links)
        rows.append({'name': m.name, 'category': category(m.name),
                     'objects': sum(any(slot == m for slot in getattr(o.data, 'materials', [])) for o in scene.objects),
                     'nodes': len(m.node_tree.nodes) if m.use_nodes else 0,
                     'constant_color': bool(p and not p.inputs['Base Color'].is_linked),
                     'uniform_surface_roughness': bool(p and not spatial_roughness),
                     'missing_normal': bool(p and not p.inputs['Normal'].is_linked),
                     'mapping': sorted(set(l.from_socket.name for l in m.node_tree.links if l.from_node.type == 'TEX_COORD')) if m.use_nodes else [],
                     'roughness': float(p.inputs['Roughness'].default_value) if p else None})
    data = {'source': bpy.data.filepath, 'scene': scene.name, 'objects': len(scene.objects),
            'materials': rows, 'category_counts': dict(Counter(r['category'] for r in rows)),
            'images': [{'name': i.name, 'path': i.filepath, 'packed': bool(i.packed_file), 'space': i.colorspace_settings.name} for i in bpy.data.images if i.source == 'FILE'],
            'uv_missing': [o.name for o in scene.objects if o.type == 'MESH' and not o.data.uv_layers]}
    NS['m37_baseline'] = data
    NS['m37_signature'] = signature(scene)
    NS['m37_source'] = scene
    return data


def node(mat, typ, label, x=0, y=0):
    n = mat.node_tree.nodes.new(typ)
    n.label = label
    n.location = (x, y)
    return n


def link(mat, out, inp):
    mat.node_tree.links.new(out, inp)


def noise(mat, coord, scale, label, detail=3):
    n = node(mat, 'ShaderNodeTexNoise', label, -800, -100)
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    n.inputs['Roughness'].default_value = .65
    link(mat, coord, n.inputs['Vector'])
    return n.outputs['Factor']


def ramp(mat, factor, stops, label):
    n = node(mat, 'ShaderNodeValToRGB', label, -400, 200)
    r = n.color_ramp
    for e in list(r.elements)[2:]: r.elements.remove(e)
    r.elements[0].position, r.elements[0].color = stops[0]
    r.elements[1].position, r.elements[1].color = stops[-1]
    for pos, col in stops[1:-1]: r.elements.new(pos).color = col
    link(mat, factor, n.inputs[0])
    return n.outputs['Color']


def mathnode(mat, operation, a, b=None, label=''):
    n = node(mat, 'ShaderNodeMath', label or operation, -600, -350)
    enum(n, 'operation', operation)
    for index, v in enumerate([a, b]):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[index].default_value = v
        else: link(mat, v, n.inputs[index])
    return n.outputs[0]


def scaled(mat, coord, scale):
    n = node(mat, 'ShaderNodeVectorMath', 'Metric directional mapping', -1000, 0)
    enum(n, 'operation', 'MULTIPLY')
    n.inputs[1].default_value = scale
    link(mat, coord, n.inputs[0])
    return n.outputs[0]


def mix(mat, fac, a, b, operation='MIX', label=''):
    n = node(mat, 'ShaderNodeMixRGB', label or operation, -150, 200)
    enum(n, 'blend_type', operation)
    for index, value in enumerate([fac, a, b]):
        if isinstance(value, (int, float)): n.inputs[index].default_value = value
        elif isinstance(value, (list, tuple)): n.inputs[index].default_value = value
        else: link(mat, value, n.inputs[index])
    return n.outputs[0]


def image_map(mat, asset, suffix, coord):
    src = next(n.image for n in bpy.data.materials[asset].node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name.endswith('_' + suffix))
    n = node(mat, 'ShaderNodeTexImage', 'CC0 ' + asset + ' / ' + suffix, -650, 450)
    n.image = src
    enum(n, 'projection', 'BOX')
    n.projection_blend = .22
    link(mat, coord, n.inputs['Vector'])
    return n.outputs['Color']


def bump(mat, height, strength, distance, normal=None):
    n = node(mat, 'ShaderNodeBump', 'Normal from height; no mesh displacement', 150, -150)
    n.inputs['Strength'].default_value = strength
    n.inputs['Distance'].default_value = distance
    link(mat, height, n.inputs['Height'])
    if normal: link(mat, normal, n.inputs['Normal'])
    return n.outputs['Normal']


def material(source, kind=None, axis=0, metric_scale=(1,1,1)):
    kind = kind or category(source.name)
    if kind=='Water' and source.use_nodes and source.node_tree.animation_data:
        # Copy the complete animated graph; changing its coordinate driver would alter the existing animation.
        m=source.copy();m.name='M37 | '+source.name
        p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        p.inputs['IOR'].default_value=1.333;p.inputs['Metallic'].default_value=0
        p.inputs['Transmission Weight'].default_value=.32
        p.inputs['Coat Weight'].default_value=.25;p.inputs['Coat Roughness'].default_value=.12
        p.inputs['Specular IOR Level'].default_value=.5
        flow=next(n for n in m.node_tree.nodes if n.type=='TEX_NOISE')
        link(m,ramp(m,flow.outputs['Factor'],[(0,(.10,)*3+(1,)),(1,(.19,)*3+(1,))],'Animated water surface roughness'),p.inputs['Roughness'])
        oldnormal=p.inputs['Normal'].links[0].from_socket if p.inputs['Normal'].is_linked else None
        geom=node(m,'ShaderNodeNewGeometry','World-metric water micro ripple',-1200,-600)
        micro=noise(m,geom.outputs['Position'],28,'Water micro ripple')
        link(m,bump(m,micro,.08,.005,oldnormal),p.inputs['Normal'])
        for r in [n for n in m.node_tree.nodes if n.type=='VALTORGB' and n.label!='Animated water surface roughness']:
            for e in r.color_ramp.elements:
                t=e.position;e.color=(.055+.145*t,.36+.29*t,.42+.30*t,1)
        m['phase']='3.7';m['material_category']='Water';m['godot_compatibility']='GODOT_SHADER_REWRITE'
        m['mapping']='Original animated Generated mapping retained; world-metric secondary ripple'
        m['animation_preserved']=True
        return m
    m = bpy.data.materials.new('M37 | ' + source.name + ((' | axis ' + str(axis)) if kind == 'Wood' else ''))
    m.use_nodes = True
    m.node_tree.nodes.clear()
    p = node(m, 'ShaderNodeBsdfPrincipled', 'Stylized PBR / Eevee', 450, 120)
    out = node(m, 'ShaderNodeOutputMaterial', 'Surface', 800, 120)
    link(m, p.outputs[0], out.inputs['Surface'])
    oldp = next((n for n in source.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if source.use_nodes else None
    base = tuple(oldp.inputs['Base Color'].default_value) if oldp else tuple(source.diffuse_color)
    p.inputs['Specular IOR Level'].default_value = .32
    geom = node(m, 'ShaderNodeNewGeometry', 'World metres: stable texture density', -1250, 0)
    coord = geom.outputs['Position']
    if kind == 'Wood':
        transform=node(m,'ShaderNodeVectorTransform','Local timber axes with physical scale compensation',-1200,-250)
        enum(transform,'vector_type','POINT');enum(transform,'convert_from','WORLD');enum(transform,'convert_to','OBJECT')
        link(m,coord,transform.inputs['Vector'])
        coord=scaled(m,transform.outputs['Vector'],metric_scale)
        phase=node(m,'ShaderNodeObjectInfo','Per-piece grain phase',-1150,-550)
        jitter=mathnode(m,'MULTIPLY',phase.outputs['Random'],17)
        shift=node(m,'ShaderNodeVectorMath','Break repeated board patterns',-1050,-550)
        enum(shift,'operation','ADD');link(m,coord,shift.inputs[0]);link(m,jitter,shift.inputs[1])
        coord=shift.outputs['Vector']
    low = noise(m, coord, .75, 'Broad non-repeating tonal variation')
    fine = noise(m, coord, 35, 'Fine surface variation')
    name = source.name.lower()
    if kind == 'Rock':
        mapped = scaled(m, coord, (1 / 2.7,) * 3)
        albedo = image_map(m, 'rock_face_03', 'Diffuse', mapped)
        rough = image_map(m, 'rock_face_03', 'Rough', mapped)
        height = image_map(m, 'rock_face_03', 'Displacement', mapped)
        idx = int(name[-1]) if name[-1].isdigit() else 0
        offset = [1, .91, 1.08, .96][idx % 4]
        color = ramp(m, low, [(0, (.28*offset, .265*offset, .21*offset, 1)), (.5, (.49*offset, .46*offset, .38*offset, 1)), (1, (.68*offset, .65*offset, .55*offset, 1))], 'Cream gray limestone layers')
        bw = node(m, 'ShaderNodeRGBToBW', 'Scan mineral variation', -400, 450)
        link(m, albedo, bw.inputs[0])
        tone = ramp(m, bw.outputs[0], [(0, (.64, .64, .64, 1)), (1, (1, 1, 1, 1))], 'Retain scanned stone detail')
        color = mix(m, .7, color, tone, 'MULTIPLY', 'Scan detail over hand-graded limestone')
        strata = node(m, 'ShaderNodeTexWave', 'Distorted geological strata', -700, -300)
        enum(strata, 'bands_direction', 'Z')
        strata.inputs['Scale'].default_value = 1.1
        strata.inputs['Distortion'].default_value = 7
        strata.inputs['Detail Scale'].default_value = .6
        link(m, coord, strata.inputs['Vector'])
        stratacolor = ramp(m, strata.outputs['Factor'], [(0,(.46,.43,.36,1)),(.5,(.8,.77,.69,1)),(1,(1,1,1,1))], 'Subtle layered mineral bands')
        color = mix(m, .32, color, stratacolor, 'MULTIPLY')
        cracks = node(m, 'ShaderNodeTexVoronoi', 'Sparse natural micro fissures', -800, -800)
        enum(cracks, 'feature', 'DISTANCE_TO_EDGE')
        cracks.inputs['Scale'].default_value = 2.2
        link(m, coord, cracks.inputs['Vector'])
        fissure = mathnode(m, 'LESS_THAN', cracks.outputs['Distance'], .016)
        fissure = mathnode(m, 'MULTIPLY', fissure, mathnode(m, 'GREATER_THAN', low, .53))
        color = mix(m, mathnode(m, 'MULTIPLY', fissure, .27), color, (.12,.105,.08,1), label='Restrained crevice pigment')
        # Sparse moss restricted to upward faces, not blanket green tint.
        sep = node(m, 'ShaderNodeSeparateXYZ', 'Upward rock faces', -800, -600)
        link(m, geom.outputs['Normal'], sep.inputs[0])
        up = mathnode(m, 'GREATER_THAN', sep.outputs['Z'], .55)
        patches = ramp(m, noise(m, coord, 1.7, 'Sparse moss islands'), [(.6,(0,0,0,1)),(.76,(1,1,1,1))], 'Soft moss boundary')
        moss = mathnode(m, 'MULTIPLY', up, patches)
        color = mix(m, mathnode(m, 'MULTIPLY', moss, .5), color, (.075, .15, .038, 1), label='Sparse botanical moss')
        link(m, color, p.inputs['Base Color'])
        rr = ramp(m, rough, [(0, (.63,)*3+(1,)), (1, (.94,)*3+(1,))], 'Mineral roughness .63-.94')
        link(m, rr, p.inputs['Roughness'])
        normal = bump(m, height, .48, .10)
        normal = bump(m, mathnode(m,'SUBTRACT',1,fissure), .15, .012, normal)
        normal = bump(m, fine, .15, .014, normal)
        link(m, normal, p.inputs['Normal'])
        m['texture_source'] = 'https://polyhaven.com/a/rock_face_03 | CC0'
    elif kind == 'Wood':
        scales = [(.34, 8, 8), (8, .34, 8), (8, 8, .34)][axis]
        grain = noise(m, scaled(m, coord, scales), 3, 'Continuous directional grain', 4)
        dark = (.19, .073, .021, 1)
        light = (.52, .29, .105, 1)
        if 'trim' in name: dark, light = (.25, .12, .037, 1), (.62, .38, .15, 1)
        if 'bark' in name: dark, light = (.11, .047, .018, 1), (.33, .18, .06, 1)
        color = ramp(m, grain, [(0, dark), (.52, tuple((dark[i]+light[i])*.5 for i in range(3))+(1,)), (1, light)], 'Warm honey grain')
        info = node(m, 'ShaderNodeObjectInfo', 'Per-piece tint; grain does not restart', -500, -650)
        tint = ramp(m, info.outputs['Random'], [(0, (.76, .69, .58, 1)), (1, (1, .96, .85, 1))], 'Restrained board variation')
        color = mix(m, .35, color, tint, 'MULTIPLY')
        dot = node(m,'ShaderNodeVectorMath','Smooth versus face normal for restrained edge wear',-600,-700)
        enum(dot,'operation','DOT_PRODUCT')
        link(m,geom.outputs['Normal'],dot.inputs[0]);link(m,geom.outputs['True Normal'],dot.inputs[1])
        wear = mathnode(m,'SUBTRACT',1,mathnode(m,'ABSOLUTE',dot.outputs['Value']))
        color = mix(m,mathnode(m,'MULTIPLY',wear,.35),color,(.63,.37,.15,1),label='Subtle bevel edge wear')
        # Keep real seams in geometry. Use scanned micro grain without adding plank seams.
        mapped = scaled(m, coord, (1/1.2,)*3)
        rough = image_map(m, 'oak_wood_planks', 'Rough', mapped)
        rough = mix(m, .25, ramp(m, grain, [(0, (.4,)*3+(1,)), (1, (.64,)*3+(1,))], 'Grain roughness'), rough)
        link(m, rough, p.inputs['Roughness'])
        link(m, color, p.inputs['Base Color'])
        link(m, bump(m, grain, .23, .024), p.inputs['Normal'])
        p.inputs['Coat Weight'].default_value = .1 if 'bark' not in name else 0
        p.inputs['Coat Roughness'].default_value = .48
        m['texture_source'] = 'https://polyhaven.com/a/oak_wood_planks | CC0 | roughness only; color/grain procedural'
    elif kind == 'Fabric':
        weave_coord = scaled(m, coord, (1, 1, 1))
        waves = []
        for direction in ['X', 'Y']:
            w = node(m, 'ShaderNodeTexWave', 'Linen warp / weft ' + direction, -800, -450)
            enum(w, 'bands_direction', direction)
            w.inputs['Scale'].default_value = 35
            w.inputs['Distortion'].default_value = .4
            w.inputs['Detail Scale'].default_value = 2
            link(m, weave_coord, w.inputs['Vector'])
            waves.append(w.outputs['Factor'])
        weave = mathnode(m, 'MULTIPLY', waves[0], waves[1])
        if 'ivory' in name: base = (.71, .62, .46, 1)
        if any(t in name for t in ['lavender', 'lilac', 'moon']): base = (.245, .285, .50, 1)
        color = ramp(m, low, [(0, tuple(v*.88 for v in base[:3])+(1,)), (1, tuple(v*1.08 for v in base[:3])+(1,))], 'Cloth dye variation')
        link(m, color, p.inputs['Base Color'])
        rr = ramp(m, fine, [(0, (.73,)*3+(1,)), (1, (.91,)*3+(1,))], 'Soft textile roughness')
        link(m, rr, p.inputs['Roughness'])
        fibers = noise(m,coord,100,'Fine soft fibers',2)
        micro = mix(m,.6,fibers,weave,label='Cross weave softened by irregular fibers')
        link(m, bump(m, micro, .28, .0022), p.inputs['Normal'])
        p.inputs['Sheen Weight'].default_value = .28
        p.inputs['Sheen Roughness'].default_value = .75
        p.inputs['Specular IOR Level'].default_value = .22
    elif kind == 'Leaves' or kind == 'Flowers':
        if kind == 'Leaves':
            if 'golden' in name: base = (.24, .33, .065, 1)
            elif 'jade' in name: base = (.062, .22, .058, 1)
            elif 'moss' in name: base = (.095, .18, .03, 1)
            else: base = (.13, .31, .062, 1)
        elif 'pink' in name: base = (.78, .32, .42, 1)
        elif 'ivory' in name: base = (.86, .79, .65, 1)
        else: base = (.9, .57, .13, 1)
        tc = node(m, 'ShaderNodeTexCoord', 'Local leaf/petal gradient', -1200, 400)
        sep = node(m, 'ShaderNodeSeparateXYZ', 'Root to tip', -800, 400)
        link(m, tc.outputs['Generated'], sep.inputs[0])
        grad = ramp(m, sep.outputs['Z'], [(0, tuple(v*.63 for v in base[:3])+(1,)), (1, tuple(min(v*1.22,1) for v in base[:3])+(1,))], 'Botanical root-to-tip colors')
        color = mix(m, .13, grad, ramp(m, low, [(0,(.5,.65,.42,1)), (1,(1,1,1,1))], 'Broad hue variation'), 'MULTIPLY')
        link(m, color, p.inputs['Base Color'])
        lower = .38 if 'waxy' in name else .5 if kind == 'Leaves' else .62
        link(m, ramp(m, fine, [(0,(lower,)*3+(1,)), (1,(lower+.18,)*3+(1,))], 'Leaf/petal roughness'), p.inputs['Roughness'])
        link(m, bump(m, noise(m,coord,65,'Botanical micro texture'),.06,.002),p.inputs['Normal'])
        p.inputs['Subsurface Weight'].default_value = .08 if kind == 'Leaves' else .12
        p.inputs['Subsurface Scale'].default_value = .015
        p.inputs['Subsurface Radius'].default_value = (.5,1,.3)
    elif kind == 'Water' and 'foam' not in name:
        p.inputs['IOR'].default_value = 1.333
        p.inputs['Transmission Weight'].default_value = .25 if 'pond' in name else .15
        p.inputs['Coat Weight'].default_value = .2
        p.inputs['Coat Roughness'].default_value = .14
        depth = node(m, 'ShaderNodeTexCoord', 'Art-directed depth proxy; not physical bathymetry', -1200, 350)
        sep = node(m, 'ShaderNodeSeparateXYZ', 'Local water depth proxy', -850,350)
        link(m, depth.outputs['Generated'], sep.inputs[0])
        fac = sep.outputs['Y'] if 'sea' in name else low
        link(m,ramp(m,fac,[(0,(.018,.19,.21,1)),(.5,(.025,.33,.36,1)),(1,(.08,.49,.44,1))],'Turquoise water depth grade'),p.inputs['Base Color'])
        ripple = noise(m, scaled(m,coord,(1,2,.2)), 4, 'Wind ripple normal')
        normal = bump(m,ripple,.24,.032)
        link(m,bump(m,fine,.08,.006,normal),p.inputs['Normal'])
        link(m,ramp(m,ripple,[(0,(.14,)*3+(1,)),(1,(.24,)*3+(1,))],'Water roughness'),p.inputs['Roughness'])
    else:
        link(m,ramp(m,low,[(0,tuple(v*.86 for v in base[:3])+(1,)),(1,tuple(min(v*1.04,1) for v in base[:3])+(1,))],'Subtle material color variation'),p.inputs['Base Color'])
        roughness = .88 if kind == 'Ground' else .62
        if 'ceramic' in name: roughness = .3; p.inputs['Coat Weight'].default_value=.3
        if 'terracotta' in name: roughness=.78
        if kind == 'Metal': roughness=.36; p.inputs['Metallic'].default_value=.8
        if kind == 'Glass':
            roughness=.16
            p.inputs['Transmission Weight'].default_value=.7
            p.inputs['IOR'].default_value=1.45
            p.inputs['Alpha'].default_value=.3
        link(m,ramp(m,fine,[(0,(roughness-.08,)*3+(1,)),(1,(min(roughness+.08,1),)*3+(1,))],'Surface roughness'),p.inputs['Roughness'])
        link(m,bump(m,fine,.1,.008 if kind == 'Ground' else .003),p.inputs['Normal'])
    m.diffuse_color = tuple(base)
    m['phase'] = '3.7'
    m['material_category'] = kind
    m['godot_compatibility'] = 'GODOT_SHADER_REWRITE' if kind == 'Water' and 'foam' not in name else 'BAKE_REQUIRED'
    m['mapping'] = 'World Position in metres; box-projected scan where used; no geometric displacement'
    # Arrange nodes in predictable columns without overlapping the BSDF/output.
    columns = {}
    for n in m.node_tree.nodes:
        x = n.location.x
        col = round(x/250)*250
        index = columns.get(col, 0)
        columns[col] = index+1
        n.location = (col,index*-230)
    return m


def import_library():
    with bpy.data.libraries.load(ROOT+'/Catmosphere_CC0_Material_Library.blend',link=False) as (src,dst):
        dst.materials = [n for n in ['rock_face_03','oak_wood_planks'] if n not in bpy.data.materials]
    for asset in ['rock_face_03','oak_wood_planks']: bpy.data.materials[asset].use_fake_user=True


def test_scene(kind, objects):
    s=bpy.data.scenes.new('M37_Test_'+kind)
    try: s.render.engine=NS['m37_source'].render.engine
    except TypeError as e: raise RuntimeError(str(e))
    s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100
    s.view_settings.view_transform=NS['m37_source'].view_settings.view_transform
    s.view_settings.exposure=0;s.view_settings.gamma=1
    s.world=bpy.data.worlds.new('M37 Neutral studio '+kind);s.world.use_nodes=True
    bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.16,.18,.20,1);bg.inputs['Strength'].default_value=.4
    copies=[]
    pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    center=sum(pts,Vector())/len(pts)
    for o in objects:
        c=o.copy();c.data=o.data.copy();c.name='M37_Prototype_'+o.name
        c.animation_data_clear();c.parent=None;c.matrix_world=o.matrix_world.copy()
        c.location-=center;s.collection.objects.link(c);copies.append(c)
    s.view_layers[0].update()
    pts=[o.matrix_world@Vector(c) for o in copies for c in o.bound_box]
    minimum=Vector(tuple(min(p[a] for p in pts) for a in range(3)))
    maximum=Vector(tuple(max(p[a] for p in pts) for a in range(3)))
    size=maximum-minimum
    target=(minimum+maximum)*.5
    cam=bpy.data.objects.new('M37 test camera '+kind,bpy.data.cameras.new('M37 camera '+kind));s.collection.objects.link(cam)
    direction=Vector((1,-2,1.25)) if kind!='Wood' else Vector((.3,-1,2.2))
    cam.location=target+direction.normalized()*max(size)*2
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    enum(cam.data,'type','ORTHO');cam.data.ortho_scale=max(size)*1.26
    s.camera=cam
    for label,loc,energy,area in [('Key',(-3,-4,6),650,5),('Rim',(3,2,4),400,4)]:
        light=bpy.data.objects.new('M37 '+label+' '+kind,bpy.data.lights.new('M37 '+label+' '+kind,'AREA'))
        s.collection.objects.link(light);light.location=loc;light.data.energy=energy;light.data.size=area
        light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
    NS['m37_tests'][kind]=(s,copies)
    return s


def render(scene, name, camera=None, size=None):
    old=(scene.camera,scene.render.filepath,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
    try:
        if camera: scene.camera=bpy.data.objects[camera]
        if size: scene.render.resolution_x,scene.render.resolution_y=size
        scene.render.resolution_percentage=100
        scene.render.filepath=ROOT+'/renders/'+name+'.png'
        bpy.ops.render.render(write_still=True,scene=scene.name)
        print('RENDERED',scene.render.filepath)
    finally:
        scene.camera,scene.render.filepath,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=old


def apply_prototype(kind):
    cache=NS.setdefault('m37_materials',{})
    for o in NS['m37_tests'][kind][1]:
        for slot in o.material_slots:
            if not slot.material: continue
            source=slot.material
            if category(source.name) != kind: continue
            axis=0
            key=(source.name,kind,axis)
            if key not in cache: cache[key]=material(source,kind,axis)
            slot.material=cache[key]
    print('Prototype ready',kind)


NS['m37_api']={'audit':audit,'material':material,'import_library':import_library,'test_scene':test_scene,'render':render,'apply_prototype':apply_prototype,'signature':signature,'category':category}
print('Phase 3.7 live-Blender helpers loaded')
