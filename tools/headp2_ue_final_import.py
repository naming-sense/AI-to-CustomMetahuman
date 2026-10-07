import unreal,json
from pathlib import Path
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');folder='/Game/Characters/HeadP2MetaHuman/Rig/HeadP2'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
previous=unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX');unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
try:
 task=unreal.AssetImportTask();task.filename=str(out/'HeadP2_Complete_CM.fbx');task.destination_path=folder;task.destination_name='SK_HeadP2';task.automated=True;task.replace_existing=False;task.save=True;task.factory=unreal.FbxFactory()
 options=unreal.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=True;options.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;options.automated_import_should_detect_type=False;options.import_materials=False;options.import_textures=False;options.import_animations=False;options.create_physics_asset=False;options.skeleton=None
 data=options.get_editor_property('skeletal_mesh_import_data')
 for key,value in {'import_morph_targets':True,'import_mesh_lods':False,'normal_import_method':unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,'preserve_smoothing_groups':True,'update_skeleton_reference_pose':False,'convert_scene_unit':True,'convert_scene':True,'morph_threshold_position':0.0}.items():data.set_editor_property(key,value)
 task.options=options;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=next((unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.SkeletalMesh)),None)
 if mesh is None:raise RuntimeError('No skeletal mesh imported')
finally:unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX '+('1' if previous else '0'))
dna_task=unreal.AssetImportTask();dna_task.filename=str(out/'HeadP2_Complete.dna');dna_task.destination_path=folder;dna_task.destination_name='HeadP2_DNA';dna_task.automated=True;dna_task.save=True;dna_task.factory=unreal.DNAAssetImportFactory();dna_options=unreal.DNAAssetImportUI();dna_options.skeletal_mesh=mesh;dna_task.options=dna_options;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([dna_task])
post=unreal.load_asset('/MetaHumanCharacter/Face/ABP_Face_PostProcess');mesh.set_editor_property('post_process_anim_blueprint',post.generated_class());skeleton=mesh.get_editor_property('skeleton');skeleton.add_compatible_skeleton(post.get_editor_property('target_skeleton'))
material=unreal.load_asset('/Game/Characters/HeadP2MetaHuman/Source/M_HeadP2_Source');materials=mesh.get_editor_property('materials')
for slot in materials:
 slot.material_interface=unreal.load_asset('/Game/Characters/HeadP2MetaHuman/Source/M_HeadP2_Eye') if 'Eye' in str(slot.material_slot_name) else material
mesh.set_editor_property('materials',materials);unreal.EditorAssetLibrary.save_loaded_asset(skeleton);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
report={'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'morphs':len(mesh.get_all_morph_target_names()),'user_data':[a.get_class().get_name() for a in mesh.get_editor_property('asset_user_data')],'live_evaluation_verified':False}
(out/'unreal_final_import.json').write_text(json.dumps(report,indent=2));(out/'unreal_final_morph_names.json').write_text(json.dumps([str(x) for x in mesh.get_all_morph_target_names()]));print('FINAL_IMPORT',json.dumps(report))
