import unreal
base='/Game/Characters/HeadP2MetaHuman/Source'
task=unreal.AssetImportTask();task.filename='D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology/HeadP2_Eye_Albedo.png';task.destination_path=base;task.destination_name='T_HeadP2_Eye';task.automated=True;task.save=True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);tex=unreal.load_asset(base+'/T_HeadP2_Eye')
for name,unlit in [('M_HeadP2_Eye',False),('M_HeadP2_EyeTracking',True)]:
 mat=unreal.load_asset(base+'/'+name)
 if mat is None:mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,base,unreal.Material,unreal.MaterialFactoryNew())
 unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
 mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT if unlit else unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
 node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-300,0);node.texture=tex
 unreal.MaterialEditingLibrary.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR if unlit else unreal.MaterialProperty.MP_BASE_COLOR)
 rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,200);rough.r=.22;unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
print('EYE_MATERIAL_READY')
