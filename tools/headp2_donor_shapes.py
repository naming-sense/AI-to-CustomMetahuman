import bpy,importlib,addon_utils,json
from pathlib import Path
module='bl_ext.api_portal_polyhammer_com.character_dna'
addon_utils.enable(module,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'Ettore_Donor.blend'))
u=importlib.import_module(module+'.utilities');io=importlib.import_module(module+'.dna_io')
i=u.get_active_rig_instance();i.head_initialize();r=i.head_dna_reader
count=0
for mesh_index in r.getMeshIndicesForLOD(0):
 obj=i.head_mesh_index_lookup.get(mesh_index)
 if not obj:continue
 mesh_name=r.getMeshName(mesh_index)
 for target in range(r.getBlendShapeTargetCount(mesh_index)):
  channel=r.getBlendShapeChannelIndex(mesh_index,target); name=r.getBlendShapeChannelName(channel)
  io.create_shape_key(index=target,mesh_index=mesh_index,mesh_object=obj,reader=r,name=name,prefix=mesh_name+'__',linear_modifier=.01)
  count+=1
print('SHAPES_CREATED',count,flush=True)
i.data.pop(i.cache_key('head','shape_key_blocks'),None)
i.head_initialize();i.evaluate(component='head')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ettore_Donor_Full.blend'),relative_remap=False)
print('FULL_DONOR_SAVED',flush=True)
