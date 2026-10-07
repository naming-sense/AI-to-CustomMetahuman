import unreal,json
from pathlib import Path
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
seq=unreal.load_asset('/Game/Characters/HeadP2MetaHuman/Rig/HeadP2/LS_HeadP2_FaceControls')
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',seq.get_bindings()[0].get_id());objects=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(bid)
if not objects:raise RuntimeError('No sequence actor bound')
actor=objects[0];c=actor.get_component_by_class(unreal.SkeletalMeshComponent);post=c.get_post_process_instance()
frame=unreal.LevelSequenceEditorBlueprintLibrary.get_current_time();report={'frame':frame,'bones':c.get_num_bones(),'postprocess':post.get_class().get_name() if post else None,'transforms':{},'curves':{}}
for bone in [str(c.get_bone_name(0)),'FACIAL_C_Jaw','FACIAL_L_EyelidUpperA2','FACIAL_L_LipCorner']:
 t=c.get_bone_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT);report['transforms'][bone]={'translation':[t.translation.x,t.translation.y,t.translation.z],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z],'rotation':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]}
for name in ['CTRL_expressions_jawOpen','CTRL_expressions_eyeBlinkL','CTRL_expressions_mouthCornerPullL','head_lod0_mesh__p2_bs_0000']:
 report['curves'][name]=c.get_curve_value(name,0.0)
names=json.loads((out/'unreal_final_morph_names.json').read_text());report['morph_weights']={n:float(c.get_curve_value(n,0.0) or 0.0) for n in names};report['active_morphs']=sum(abs(v)>1e-6 for v in report['morph_weights'].values())
(out/('unreal_delivery_pose_'+str(frame)+'.json')).write_text(json.dumps(report,indent=2));print('POSE',json.dumps({k:v for k,v in report.items() if k!='morph_weights'}))
