# -*- coding: utf-8 -*-
"""Refine water texture frequency and verify prototype, without touching source assets."""
import bpy, math, json
ROOT='C:/Game/GameModel_3D'
NS=bpy.app.driver_namespace

def refine():
    photo=bpy.data.images.load(ROOT+'/textures/water/oga_waterfall_1.png',check_existing=True)
    photo.colorspace_settings.name='Non-Color';photo.pack()
    for m in bpy.data.materials:
        if not m.name.startswith(('W39 | layered','W39 | white')):continue
        for n in m.node_tree.nodes:
            if n.bl_idname=='ShaderNodeVectorMath' and n.operation=='MULTIPLY':n.inputs[1].default_value=(1.6,2.6,1)
            if m.name.startswith('W39 | white') and n.type=='TEX_IMAGE' and n.image and 'height' in n.image.name:
                n.image=photo;n.label='CC0 photographed waterfall luminance / foam mask'
            if m.name.startswith('W39 | white') and n.type=='MAP_RANGE':
                n.inputs['From Min'].default_value=.22;n.inputs['From Max'].default_value=.72
                n.inputs['To Min'].default_value=0;n.inputs['To Max'].default_value=.88
    c=bpy.data.collections['W39 | Pass A Waterfall Prototype']
    for o in c.objects:
        if o.name.startswith('W39 foam'):
            o.location.x+=.2;o.location.y-=.22
        if o.name.startswith('W39 splash'):
            for d in o.animation_data.drivers:
                if d.data_path=='location' and d.array_index==0:d.driver.expression='0.2+('+d.driver.expression+')'
                if d.data_path=='location' and d.array_index==1:d.driver.expression='-0.22+('+d.driver.expression+')'
    # Freeze only copied contextual old-water shaders inside the review scene.
    # Original main-scene objects, materials and drivers remain intact.
    preview=bpy.data.scenes['W39 | Prototype Animation Review']
    for o in list(preview.collection.objects):
        if o.type!='MESH' or not any(m and 'flowing water lane' in m.name for m in o.data.materials):continue
        dup=o.copy();dup.data=o.data.copy();dup.name='W39 review static context | '+o.name
        for idx,m in enumerate(dup.data.materials):
            if m and m.node_tree and m.node_tree.animation_data:
                nm=m.copy();nm.name='W39 review static shader | '+m.name
                for d in list(nm.node_tree.animation_data.drivers):
                    node_path=d.data_path;expr=d.driver.expression
                    value=eval(expr,{'__builtins__':{}},{'frame':75})
                    socket_path=node_path.rsplit('.',1)[0];socket=nm.node_tree.path_resolve(socket_path)
                    socket.default_value[d.array_index]=value
                    nm.node_tree.driver_remove(node_path,d.array_index)
                dup.data.materials[idx]=nm
        preview.collection.objects.unlink(o);preview.collection.objects.link(dup)
    print('REFINED_EXTERNAL_FOAM',tuple(photo.size))

def collision_audit():
    from mathutils.bvhtree import BVHTree
    c=bpy.data.collections['W39 | Pass A Waterfall Prototype'];out=[]
    for w in c.objects:
        if not w.name.startswith(('W39 main','W39 detached','W39 aerated')):continue
        tree=BVHTree.FromPolygons([w.matrix_world@v.co for v in w.data.vertices],[tuple(p.vertices) for p in w.data.polygons])
        for name,t in NS.get('w39_clearance_trees',[]):
            overlap=tree.overlap(t)
            if overlap:out.append([w.name,name,len(overlap)])
    print('COLLISION_CANDIDATES',out)
    NS['w39_final_collision']=out

NS['w39_finalize']={'refine':refine,'collision_audit':collision_audit}
