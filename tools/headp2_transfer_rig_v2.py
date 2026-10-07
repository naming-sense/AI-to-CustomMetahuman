import bpy,importlib,addon_utils,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
u=importlib.import_module(module+'.utilities');io=importlib.import_module(module+'.dna_io')
bpy.ops.wm.open_mainfile(filepath=str(out/'Ettore_Donor_Full.blend'))
instance=u.get_active_rig_instance();instance.head_initialize();instance.auto_evaluate=False
head=instance.head_mesh;rig=instance.head_rig
sources=[head,bpy.data.objects['Ettore_teeth_lod0_mesh']]
with bpy.data.libraries.load(str(out/'Head_P2_EyeRepair_Work.blend'),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n in ['HeadP2_EyeRepair_Surface','HeadP2_eyeLeft','HeadP2_eyeRight']]
loaded={o.name:o for o in dst.objects}
for obj in loaded.values():bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.update()
target=loaded['HeadP2_EyeRepair_Surface'];original_matrix=target.matrix_world.copy();target.data.transform(original_matrix);target.matrix_world=Matrix.Identity(4)
positions=np.array([v.co[:] for v in target.data.vertices],dtype=np.float32)
components=np.array([x.value for x in target.data.attributes['p2_source_component'].data])
def warp(points):
 p=np.asarray(points,dtype=np.float32);result=p.copy()
 for side in [-1,1]:
  center=np.array([side*.0292,-.096,1.617],dtype=np.float32)
  relative=p-center;falloff=np.exp(-np.sum((relative/np.array([.032,.04,.026]))**2,axis=1)*1.5)
  shift=np.column_stack((relative[:,0]*.25+side*.0033,np.full(len(p),-.003),relative[:,2]*.6+.0005))
  result+=shift*falloff[:,None]
 relative=p-np.array([0,-.112,1.546]);falloff=np.exp(-np.sum((relative/np.array([.035,.035,.022]))**2,axis=1)*1.5)
 result+=np.column_stack((-relative[:,0]*.12,np.zeros(len(p)),relative[:,2]*.4+.002))*falloff[:,None]
 return result
weights=[{} for _ in positions];shape_deltas={};mapping_report={}
for source_index,source in enumerate(sources):
 source.data.calc_loop_triangles();triangles=np.array([t.vertices[:] for t in source.data.loop_triangles],dtype=np.int32)
 base=np.array([v.co[:] for v in source.data.vertices],dtype=np.float32)
 fitted=warp(base)
 tree=BVHTree.FromPolygons([Vector(v) for v in fitted],triangles.tolist(),all_triangles=True)
 selected=np.where(np.isin(components,[1,2,4,6]) if source_index else ~np.isin(components,[1,2,4,6]))[0]
 indices=[];barys=[];distances=[]
 for index in selected:
  point,normal,tri,distance=tree.find_nearest(Vector(positions[index]))
  target_normal=target.data.vertices[index].normal
  candidates=tree.find_nearest_range(Vector(positions[index]),distance+.003)
  if candidates:
   point,normal,tri,distance=min(candidates,key=lambda hit:hit[3]**2+(.004*(1-max(-1,min(1,target_normal.dot(hit[1])))))**2)
  ids=triangles[tri];a,b,c=fitted[ids]
  v0=b-a;v1=c-a;v2=np.array(point)-a
  d00=v0@v0;d01=v0@v1;d11=v1@v1;denom=d00*d11-d01*d01
  if abs(denom)<1e-18:w=np.array([1.,0,0])
  else:
   v=(d11*(v2@v0)-d01*(v2@v1))/denom;w2=(d00*(v2@v1)-d01*(v2@v0))/denom;w=np.clip([1-v-w2,v,w2],0,1);w/=w.sum()
  indices.append(ids);barys.append(w);distances.append(distance)
  for vertex_id,weight in zip(ids,w):
   for group in source.data.vertices[vertex_id].groups:
    name=source.vertex_groups[group.group].name
    weights[index][name]=weights[index].get(name,0)+float(weight)*group.weight
 indices=np.array(indices);barys=np.array(barys,dtype=np.float32)
 if float(np.median(distances))>.04:raise RuntimeError('Surface correspondence distance exceeds 4 cm')
 mapping_report[source.name]={'mapped_vertices':len(selected),'median_distance_m':float(np.median(distances)),'max_distance_m':float(max(distances))}
 if source.data.shape_keys:
  for key in list(source.data.shape_keys.key_blocks)[1:]:
   channel=key.name.split('__',1)[-1]
   flat=np.empty(len(base)*3,dtype=np.float32);key.data.foreach_get('co',flat)
   delta=warp(flat.reshape(-1,3))-fitted
   values=(delta[indices]*barys[:,:,None]).sum(axis=1)
   shape_deltas.setdefault(channel,np.zeros_like(positions))[selected]=values
 print('MAPPED',source.name,len(selected),flush=True)
# Fit neutral joint positions in the same smooth field as the transfer surface.
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for bone in rig.data.edit_bones:
 offset=Vector(warp(np.array([bone.head[:]]))[0])-bone.head
 bone.head+=offset;bone.tail+=offset
bpy.ops.object.mode_set(mode='OBJECT')
# Attach the authored surface to the existing rig instance, retaining face-board metadata.
old_data=head.data;head.data=target.data;head.matrix_world=Matrix.Identity(4)
for group in list(head.vertex_groups):head.vertex_groups.remove(group)
groups={};max_error=0
for index,weight_dict in enumerate(weights):
 active=sorted(((name,value) for name,value in weight_dict.items() if value>1e-5),key=lambda p:p[1],reverse=True)[:12]
 total=sum(value for _,value in active)
 if total<=0:raise RuntimeError('Unweighted vertex '+str(index))
 for name,value in active:
  if name not in groups:groups[name]=head.vertex_groups.new(name=name)
  groups[name].add([index],value/total,'REPLACE')
 max_error=max(max_error,abs(sum(value/total for _,value in active)-1))
head.shape_key_add(name='Basis',from_mix=False)
for channel,delta in shape_deltas.items():
 key=head.shape_key_add(name='head_lod0_mesh__'+channel,from_mix=False);key.data.foreach_set('co',(positions+delta).ravel());key.value=0
bpy.data.objects.remove(target,do_unlink=True)
# Replace the eye geometry only; the donor skin group order and UV topology are identical.
for suffix in ['Left','Right']:
 original=bpy.data.objects['Ettore_eye'+suffix+'_lod0_mesh'];replacement=loaded['HeadP2_eye'+suffix]
 old_positions=np.array([v.co[:] for v in original.data.vertices],dtype=np.float32)
 old_center=(old_positions.min(0)+old_positions.max(0))/2
 eye_shapes=[]
 if original.data.shape_keys:
  for key in list(original.data.shape_keys.key_blocks)[1:]:
   flat=np.empty(len(old_positions)*3,dtype=np.float32);key.data.foreach_get('co',flat);eye_shapes.append((key.name,(flat.reshape(-1,3)-old_positions)*1.35))
 original.shape_key_clear();original.data=replacement.data.copy();original.matrix_world=Matrix.Identity(4)
 new_positions=np.array([v.co[:] for v in original.data.vertices],dtype=np.float32)
 new_center=(new_positions.min(0)+new_positions.max(0))/2
 original.shape_key_add(name='Basis')
 for name,delta in eye_shapes:
  key=original.shape_key_add(name=name);key.data.foreach_set('co',(new_positions+delta).ravel())
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 bone=rig.data.edit_bones['FACIAL_'+('L' if suffix=='Left' else 'R')+'_EyeParallel']
 offset=Vector(new_center)-bone.head
 for joint in [bone]+list(bone.children_recursive):joint.head+=offset;joint.tail+=offset
 bpy.ops.object.mode_set(mode='OBJECT')
 bpy.data.objects.remove(replacement,do_unlink=True)
 # Translate the eyeball joint pivot to the new eyeball center, retaining its orientation.
 eye_names=[g.name for g in original.vertex_groups if 'Eye' in g.name]
 print('EYE_GROUPS',suffix,eye_names,flush=True)
# Exclude auxiliary donor surfaces; the authored P2 mouth parts remain in the main mesh.
allowed={head.name,rig.name,'Ettore_eyeLeft_lod0_mesh','Ettore_eyeRight_lod0_mesh'}
for item in instance.output.head_item_list:item.include=bool(item.scene_object and item.scene_object.name in allowed)
for obj in bpy.data.objects:
 if obj.type=='MESH' and obj.name.startswith('Ettore_') and obj.name not in allowed:obj.hide_render=True;obj.hide_set(True)
instance.output.folder_path=str(out);instance.output.method='overwrite';instance.output.component='head';instance.output.run_validations=True
exporter=io.DNAExporter(instance=instance,linear_modifier=.01,file_name='HeadP2_Custom_v2.dna',component_type='head',textures=False,vertex_colors=False,seam_follower=None)
result=exporter.run();print('DNA_EXPORT',result[:3],flush=True)
if not result[0]:raise RuntimeError(str(result[:3]))
reader=io.get_dna_reader(file_path=out/'HeadP2_Custom_v2.dna',file_format='binary',data_layer='All')
report={'stage':'initial_transfer_candidate','mapping':mapping_report,'surface_vertices':len(head.data.vertices),'surface_faces':len(head.data.polygons),'shape_keys':len(shape_deltas),'weight_sum_error':max_error,'dna_joints':reader.getJointCount(),'dna_channels':reader.getBlendShapeChannelCount(),'dna_meshes':[reader.getMeshName(x) for x in range(reader.getMeshCount())],'deformation_review_passed':False}
(out/'transfer_candidate_v2.json').write_text(json.dumps(report,indent=2))
instance.head_dna_file_path=str(out/'HeadP2_Custom_v2.dna');instance.destroy_references();instance.head_initialize();instance.auto_evaluate=True;instance.evaluate(component='head')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Head_P2_Rig_Candidate_v2.blend'),relative_remap=False)
print('CANDIDATE_SAVED',json.dumps(report),flush=True)
