import bpy,addon_utils,importlib,json
from pathlib import Path
m='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(m,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
i=importlib.import_module(m+'.utilities').get_active_rig_instance();engine=importlib.import_module(m+'.runtime.engine');i.head_initialize()
controls=['CTRL_C_jaw','CTRL_L_eye_blink','CTRL_R_eye_blink','CTRL_L_mouth_cornerPull','CTRL_R_mouth_cornerPull'];report={}
for frame,values in [(0,{}),(20,{'CTRL_C_jaw':.7}),(60,{'CTRL_L_eye_blink':1,'CTRL_R_eye_blink':1}),(100,{'CTRL_L_mouth_cornerPull':.7,'CTRL_R_mouth_cornerPull':.7})]:
 for name in controls:i.face_board.pose.bones[name].location.y=values.get(name,0)
 i.face_board.update_tag();i.evaluate(component='head');bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rig=i.head_rig.evaluated_get(deps)
 joints={}
 for name in ['FACIAL_C_Jaw','FACIAL_L_EyelidUpperA2','FACIAL_L_LipCorner']:
  p=rig.matrix_world@rig.pose.bones[name].matrix.translation;joints[name]=[p.x*100,-p.y*100,p.z*100]
 raw={i.head_dna_reader.getRawControlName(j).replace('.','_'):engine.ui_raw_control_value(i,j,deps) for j in range(i.head_dna_reader.getRawControlCount())}
 report[str(frame)]={'joints_cm':joints,'raw_controls':raw,'shape_values':{key.name:key.value for key in i.head_mesh.data.shape_keys.key_blocks[1:]}}
(out/'blender_cross_engine.json').write_text(json.dumps(report,indent=2));print('CROSS_ENGINE_RECORDED',flush=True)
