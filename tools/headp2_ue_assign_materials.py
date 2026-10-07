import unreal
path='/Game/Characters/HeadP2MetaHuman/Rig/HeadP2/SK_HeadP2'
mesh=unreal.load_asset(path);slots=mesh.get_editor_property('materials')
for j in range(len(slots)):
 slot=slots[j];name='M_HeadP2_Eye' if 'Eye' in str(slot.material_slot_name) else 'M_HeadP2_Source'
 slot.set_editor_property('material_interface',unreal.load_asset('/Game/Characters/HeadP2MetaHuman/Source/'+name));slots[j]=slot
mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
for slot in mesh.get_editor_property('materials'):print('SAVED_SLOT',str(slot.material_slot_name),str(slot.material_interface))
