import unreal,json
from pathlib import Path
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
folder='/Game/Characters/HeadP2MetaHuman/Rig/HeadP2'
mesh=unreal.load_asset(folder+'/SK_HeadP2')
assets=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
sequence=assets.create_asset('LS_HeadP2_FaceControls',folder,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
if sequence is None:raise RuntimeError('Sequence already exists; inspect before changing')
sequence.set_display_rate(unreal.FrameRate(30,1));sequence.set_playback_start(0);sequence.set_playback_end(120)
actor=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(0,0,0),unreal.Rotator(0,0,0),transient=True)
try:
 actor.set_actor_label('HeadP2 Face Controls');component=actor.get_component_by_class(unreal.SkeletalMeshComponent);component.set_skeletal_mesh_asset(mesh)
 binding=sequence.add_spawnable_from_instance(actor)
finally:actors.destroy_actor(actor)
control=unreal.load_asset('/MetaHumanCharacter/Face/Face_ControlBoard_CtrlRig')
track=unreal.ControlRigSequencerLibrary.find_or_create_control_rig_track(world,sequence,control.generated_class(),binding)
unreal.EditorAssetLibrary.save_loaded_asset(sequence)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
rigs=unreal.ControlRigSequencerLibrary.get_control_rigs(sequence)
print('RIG_COUNT',len(rigs),'TRACK',track)
rig=rigs[0].control_rig
print('FINAL_SEQUENCE_CREATED')
