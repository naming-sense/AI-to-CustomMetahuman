import bpy,importlib,addon_utils,json,numpy as np
from pathlib import Path
from mathutils import Vector
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
i=importlib.import_module(module+'.utilities').get_active_rig_instance();i.head_initialize();mesh=i.head_mesh
controls=['CTRL_C_jaw','CTRL_L_eye_blink','CTRL_R_eye_blink','CTRL_L_mouth_cornerPull','CTRL_R_mouth_cornerPull']
scene=bpy.context.scene
for obj in scene.objects:obj.hide_render=obj.name not in [mesh.name,'Ettore_eyeLeft_lod0_mesh','Ettore_eyeRight_lod0_mesh']
camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);scene.collection.objects.link(cam);cam.location=(0,-4,1.594);cam.rotation_euler=Vector((0,1,0)).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.2875;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.65,.65,.65);scene.display.shading.show_cavity=True
scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
def sample(values):
 for name in controls:i.face_board.pose.bones[name].location.y=values.get(name,0)
 i.face_board.update_tag();i.evaluate(component='head');bpy.context.view_layer.update()
 evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh();a=np.empty(len(data.vertices)*3,dtype=np.float32);data.vertices.foreach_get('co',a);evaluated.to_mesh_clear();return a.reshape(-1,3)
neutral=sample({});base=np.array([v.co[:] for v in mesh.data.vertices]);report={'neutral_max_delta_m':float(np.linalg.norm(neutral-base,axis=1).max()),'poses':{}}
for name,values in [('neutral',{}),('jaw',{'CTRL_C_jaw':.7}),('blink',{'CTRL_L_eye_blink':1,'CTRL_R_eye_blink':1}),('smile',{'CTRL_L_mouth_cornerPull':.7,'CTRL_R_mouth_cornerPull':.7})]:
 points=sample(values);delta=np.linalg.norm(points-neutral,axis=1)
 report['poses'][name]={'moved_vertices':int((delta>1e-6).sum()),'max_delta_m':float(delta.max()),'active_correctives':sum(abs(k.value)>1e-6 for k in mesh.data.shape_keys.key_blocks),'finite':bool(np.isfinite(points).all())}
 scene.render.filepath=str(out/('delivery_review_'+name+'.png'));bpy.ops.render.render(write_still=True)
ids=np.array([v.value for v in mesh.data.attributes['p2_source_vertex'].data]);source=np.load(out/'p2_positions.npy')[ids];expected=np.column_stack((source[:,1]*.25,-source[:,0]*.25-.03,source[:,2]*.25+1.594))
report['retained_source_position_max_error_m']=float(np.linalg.norm(base-expected,axis=1).max())
(out/'delivery_expression_review.json').write_text(json.dumps(report,indent=2));print('REVIEW',json.dumps(report),flush=True)
