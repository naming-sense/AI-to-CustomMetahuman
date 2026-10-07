import bpy,importlib,addon_utils,json,numpy as np
from pathlib import Path
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
u=importlib.import_module(module+'.utilities');io=importlib.import_module(module+'.dna_io');dna=importlib.import_module(module+'.bindings').dna
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig_Work.blend'))
i=u.get_active_rig_instance();i.head_initialize();i.auto_evaluate=False
source=io.get_dna_reader(file_path=Path('C:/Users/YOUR_USER/Documents/Megascans Library/Downloaded/UAssets/9qipkIPG/Tier0/asset_ue/MetaHumans/Ettore/SourceAssets/Ettore.dna'),file_format='binary',data_layer='All')
current=io.get_dna_reader(file_path=out/'HeadP2_Rig.dna',file_format='binary',data_layer='All')
writer=io.get_dna_writer(file_path=out/'HeadP2_Complete.dna',file_format='binary');writer.setFrom(current,dna.DataLayer_All,dna.UnknownLayerPolicy_Preserve,None)
channel_map=[{'index':j,'original':source.getBlendShapeChannelName(j),'alias':f'p2_bs_{j:04d}'} for j in range(source.getBlendShapeChannelCount())]
for item in channel_map:writer.setBlendShapeChannelName(index=item['index'],name=item['alias'])
source_meshes={source.getMeshName(j):j for j in range(source.getMeshCount())}
def channels(mesh_name):
 mesh_index=source_meshes[mesh_name]
 return [source.getBlendShapeChannelIndex(mesh_index,t) for t in range(source.getBlendShapeTargetCount(mesh_index))]
main_channels=channels('head_lod0_mesh')+channels('teeth_lod0_mesh')
writer.clearMeshBlendShapeChannelMappings();mapping_index=0;counts={};max_delta=0
for mesh_index in range(current.getMeshCount()):
 name=current.getMeshName(mesh_index);obj=bpy.data.objects['Ettore_'+name];keys=list(obj.data.shape_keys.key_blocks)[1:]
 indices=main_channels if mesh_index==0 else channels(name)
 if len(indices)!=len(keys):raise RuntimeError(f'Channel order mismatch {name}: {len(indices)} / {len(keys)}')
 if len(set(indices))!=len(indices):raise RuntimeError('Duplicate channel indices')
 basis=np.array([v.co[:] for v in obj.data.shape_keys.key_blocks[0].data],dtype=np.float32)
 writer.clearBlendShapeTargets(meshIndex=mesh_index)
 for target,(key,channel) in enumerate(zip(keys,indices)):
  key.name=name+'__'+channel_map[channel]['alias'];flat=np.empty(len(basis)*3,dtype=np.float32);key.data.foreach_get('co',flat);delta=flat.reshape(-1,3)-basis
  selected=np.where(np.linalg.norm(delta,axis=1)>1e-9)[0];values=delta[selected];dna_delta=np.column_stack((values[:,0],values[:,2],-values[:,1]))*100
  writer.setBlendShapeChannelIndex(meshIndex=mesh_index,blendShapeTargetIndex=target,blendShapeChannelIndex=channel)
  writer.setBlendShapeTargetVertexIndices(meshIndex=mesh_index,blendShapeTargetIndex=target,vertexIndices=selected.tolist())
  writer.setBlendShapeTargetDeltas(meshIndex=mesh_index,blendShapeTargetIndex=target,deltas=dna_delta.tolist())
  writer.setMeshBlendShapeChannelMapping(index=mapping_index,meshIndex=mesh_index,blendShapeChannelIndex=channel);mapping_index+=1
 counts[name]=len(indices)
writer.write()
if not dna.Status.isOk():raise RuntimeError(str(dna.Status.get().message))
(out/'channel_alias_map.json').write_text(json.dumps(channel_map,indent=2))
verify=io.get_dna_reader(file_path=out/'HeadP2_Complete.dna',file_format='binary',data_layer='All')
for j in range(verify.getMeshCount()):
 if verify.getBlendShapeTargetCount(j)!=counts[verify.getMeshName(j)]:raise RuntimeError('DNA target count mismatch')
i.head_dna_file_path=str(out/'HeadP2_Complete.dna');i.destroy_references();i.head_initialize();i.auto_evaluate=True;i.evaluate(component='head')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HeadP2_Rig.blend'),relative_remap=False)
bpy.ops.object.select_all(action='DESELECT')
for obj in [i.head_mesh,i.head_rig,bpy.data.objects['Ettore_eyeLeft_lod0_mesh'],bpy.data.objects['Ettore_eyeRight_lod0_mesh']]:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=i.head_mesh
bpy.ops.export_scene.fbx(filepath=str(out/'HeadP2_Complete.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},use_mesh_modifiers=False,add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',path_mode='AUTO',colors_type='NONE')
(out/'complete_channel_verification.json').write_text(json.dumps({'channels':verify.getBlendShapeChannelCount(),'mesh_targets':counts,'mapping_count':mapping_index,'joints':verify.getJointCount(),'behavior_control_count':verify.getRawControlCount()},indent=2))
print('COMPLETE_CHANNELS',counts,flush=True)
