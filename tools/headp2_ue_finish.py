import unreal,json
from pathlib import Path
folder='/Game/Characters/HeadP2MetaHuman/Rig/HeadP2';seq=unreal.load_asset(folder+'/LS_HeadP2_FaceControls')
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',seq.get_bindings()[0].get_id())
c=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(bid)[0].get_component_by_class(unreal.SkeletalMeshComponent)
c.set_editor_property('override_materials',[])
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
unreal.EditorAssetLibrary.save_loaded_asset(seq)
mesh=unreal.load_asset(folder+'/SK_HeadP2')
report={'mesh':mesh.get_path_name(),'morphs':len(mesh.get_all_morph_target_names()),'materials':[str(c.get_material(j).get_path_name()) if c.get_material(j) else None for j in range(c.get_num_materials())],'bones':c.get_num_bones(),'postprocess':c.get_post_process_instance().get_class().get_name(),'sequence':seq.get_path_name(),'current_frame':0}
assert report['morphs']==782 and all(report['materials']) and report['bones']==876
Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology/unreal_saved_state.json').write_text(json.dumps(report,indent=2))
unreal.EditorAssetLibrary.sync_browser_to_objects([seq.get_path_name(),mesh.get_path_name()])
print('SAVED_STATE',json.dumps(report))
