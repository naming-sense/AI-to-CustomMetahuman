import bpy,addon_utils,importlib,numpy as np,json
from pathlib import Path
from mathutils import Vector
m='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(m,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_SkinFix.blend'))
i=importlib.import_module(m+'.utilities').get_active_rig_instance();i.head_initialize();head=i.head_mesh;p=np.array([v.co[:] for v in head.data.vertices]);comp=np.array([v.value for v in head.data.attributes['p2_source_component'].data]);controls=['CTRL_C_jaw','CTRL_L_eye_blink','CTRL_R_eye_blink','CTRL_L_mouth_cornerPull','CTRL_R_mouth_cornerPull','CTRL_C_tongue_inOut','CTRL_C_tongue_move','CTRL_C_tongue_tipMove']
scene=bpy.context.scene
for o in scene.objects:o.hide_render=o.name not in [head.name,'Ettore_eyeLeft_lod0_mesh','Ettore_eyeRight_lod0_mesh']
camdata=bpy.data.cameras.new('SkinFixReview');cam=bpy.data.objects.new('SkinFixReview',camdata);scene.collection.objects.link(cam);cam.location=(0,-4,1.545);cam.rotation_euler=Vector((0,1,0)).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.145;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE';scene.display.shading.show_cavity=True
for mat in head.data.materials:
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image and node.image.name.endswith('_0'):mat.node_tree.nodes.active=node
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
def sample(values):
 for name in controls:
  if name in i.face_board.pose.bones:i.face_board.pose.bones[name].location=(0,values.get(name,0),0)
 i.face_board.update_tag();i.evaluate(component='head');bpy.context.view_layer.update();obj=head.evaluated_get(bpy.context.evaluated_depsgraph_get());data=obj.to_mesh();a=np.array([v.co[:] for v in data.vertices]);obj.to_mesh_clear();return a
neutral=sample({});diagnosis=json.loads((out/'lip_diagnosis.json').read_text());edges=[row['verts'] for row in diagnosis['top_stretched_edges']];report={'poses':{},'tongue_nontongue_max':0}
for v in np.where(comp==4)[0]:report['tongue_nontongue_max']=max(report['tongue_nontongue_max'],sum(g.weight for g in head.data.vertices[v].groups if 'Tongue' not in head.vertex_groups[g.group].name))
for name,values in [('neutral',{}),('jaw',{'CTRL_C_jaw':.7}),('jaw_full',{'CTRL_C_jaw':1.0}),('smile',{'CTRL_L_mouth_cornerPull':.7,'CTRL_R_mouth_cornerPull':.7}),('jaw_smile',{'CTRL_C_jaw':.7,'CTRL_L_mouth_cornerPull':.7,'CTRL_R_mouth_cornerPull':.7}),('tongue',{'CTRL_C_jaw':.7,'CTRL_C_tongue_inOut':.7}),('tongue_out',{'CTRL_C_jaw':.7,'CTRL_C_tongue_inOut':-.7})]:
 points=sample(values);growth=[float((np.linalg.norm(points[a]-points[b])-np.linalg.norm(neutral[a]-neutral[b]))*1000) for a,b in edges]
 report['poses'][name]={'max_diagnostic_edge_growth_mm':max(growth),'first_edge_mm':float(np.linalg.norm(points[edges[0][0]]-points[edges[0][1]])*1000),'tongue_center':points[comp==4].mean(0).tolist(),'finite':bool(np.isfinite(points).all())}
 scene.render.filepath=str(out/('skinfix_'+name+'.png'));bpy.ops.render.render(write_still=True)
report['pass']=report['poses']['jaw']['max_diagnostic_edge_growth_mm']<3 and report['tongue_nontongue_max']<1e-6
(out/'skin_fix_review.json').write_text(json.dumps(report,indent=2));print('SKIN_REVIEW',json.dumps(report),flush=True)
