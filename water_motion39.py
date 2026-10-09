# -*- coding: utf-8 -*-
"""Final speed calibration and sparse falling droplets for Pass A."""
import bpy, math, random
ROOT='C:/Game/GameModel_3D'
NS=bpy.app.driver_namespace
def calibrate():
    for m in bpy.data.materials:
        if m.name.startswith(('W39 | layered','W39 | white')):
            lane=int(m.name.rsplit(' ',1)[-1])
            for d in m.node_tree.animation_data.drivers:
                d.driver.expression=f'(frame-1)*{[17,23,29][lane]}/300.0'
    c=bpy.data.collections['W39 | Pass A Waterfall Prototype']
    rng=random.Random(390)
    mat=bpy.data.materials['W39 | aerated foam']
    for i in range(24):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
        o=bpy.context.object;o.name='W39 falling spray %02d'%i
        for col in list(o.users_collection):col.objects.unlink(o)
        c.objects.link(o);o.data.materials.append(mat)
        phase=rng.random();period=[30,50,60][i%3];side=rng.uniform(-.08,.16);depth=rng.uniform(-.08,.08)
        q=f'((frame-1)/{period}.0+{phase})%1.0'
        # Exterior free-fall spray, unlike the stationary flow ribbons.
        expressions=[f'5.0+0.35*({q})+{side}',f'0.95+{depth}-0.23*sin(pi*({q}))',f'9.7-6.17*pow(({q}),1.35)']
        for axis,expr in enumerate(expressions):o.driver_add('location',axis).driver.expression=expr
        size=rng.uniform(.007,.016)
        for axis in range(3):o.driver_add('scale',axis).driver.expression=f'{size*(3 if axis==2 else 1)}*sin(pi*({q}))'
    print('CALIBRATED_UV_CYCLES',17,23,29,'FALLING_SPRAY',24)
def finish():
    s=bpy.data.scenes['Scene'];p=bpy.data.scenes['W39 | Prototype Animation Review']
    NS['w39_api']['verify']()
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Catmosphere_Water_Master.blend')
    NS['w39_api']['render_after']()
    NS['w39_animation_status']='rendering final calibrated preview'
    bpy.ops.render.render(animation=True,scene=p.name)
    NS['w39_animation_status']='done final calibrated preview'
    s.frame_set(75);bpy.context.window.scene=s;s.camera=bpy.data.objects['W39_PrototypeCamera']
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Catmosphere_Water_Master.blend')
NS['w39_motion']={'calibrate':calibrate,'finish':finish}
