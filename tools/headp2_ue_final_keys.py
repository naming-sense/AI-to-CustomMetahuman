import unreal,json
from pathlib import Path
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
seq=unreal.load_asset('/Game/Characters/HeadP2MetaHuman/Rig/HeadP2/LS_HeadP2_FaceControls');rig=unreal.ControlRigSequencerLibrary.get_control_rigs(seq)[0].control_rig
controls=['CTRL_C_jaw','CTRL_L_eye_blink','CTRL_R_eye_blink','CTRL_L_mouth_cornerPull','CTRL_R_mouth_cornerPull']
for frame in [0,20,40,60,80,100,119]:
 for name in controls:
  value=.7 if frame==20 and name=='CTRL_C_jaw' else (1.0 if frame==60 and 'blink' in name else (.7 if frame==100 and 'cornerPull' in name else 0.0))
  if name=='CTRL_C_jaw':unreal.ControlRigSequencerLibrary.set_local_control_rig_vector2d(seq,rig,name,unreal.FrameNumber(frame),unreal.Vector2D(0,value))
  else:unreal.ControlRigSequencerLibrary.set_local_control_rig_float(seq,rig,name,unreal.FrameNumber(frame),value)
unreal.EditorAssetLibrary.save_loaded_asset(seq);unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
mesh=unreal.load_asset('/Game/Characters/HeadP2MetaHuman/Rig/HeadP2/SK_HeadP2')
(out/'unreal_final_morph_names.json').write_text(json.dumps([str(n) for n in mesh.get_all_morph_target_names()]))
(out/'unreal_sequence_status.json').write_text(json.dumps({'sequence':seq.get_path_name(),'control_rig':'/MetaHumanCharacter/Face/Face_ControlBoard_CtrlRig','rig_count':1,'keys_added':True,'frames':{'neutral':0,'jaw':20,'blink':60,'smile':100},'live_evaluation_verified':False},indent=2))
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for actor in actors:
 c=actor.get_component_by_class(unreal.SkeletalMeshComponent)
 if c and c.get_editor_property('skeletal_mesh_asset')==mesh:print('BOUND_ACTOR',actor.get_path_name(),'POSTPROCESS',c.get_post_process_instance(),'BONES',c.get_num_bones())
print('KEYS_SAVED')
