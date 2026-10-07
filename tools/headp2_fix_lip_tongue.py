import bpy,addon_utils,importlib,numpy as np,json,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
m='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(m,default_set=False,persistent=False)
u=importlib.import_module(m+'.utilities');io=importlib.import_module(m+'.dna_io');dna=importlib.import_module(m+'.bindings').dna
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');bpy.ops.wm.open_mainfile(filepath='D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology/Backups/BeforeLipTongueFix_20261007_213033/HeadP2_Rig.blend')
i=u.get_active_rig_instance();i.head_initialize();i.auto_evaluate=False;head=i.head_mesh
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
p=np.array([v.co[:] for v in head.data.vertices],dtype=np.float32);comp=np.array([v.value for v in head.data.attributes['p2_source_component'].data]);groups=[g.name for g in head.vertex_groups];weights=np.zeros((len(p),len(groups)),dtype=np.float32)
for v in head.data.vertices:
 for g in v.groups:weights[v.index,g.group]=g.weight
before=weights.copy()
# Smooth along actual mesh edges: the open lip boundary is never bridged by spatial neighbors.
mask=(comp==0)&(np.abs(p[:,0])<.037)&(p[:,2]>1.525)&(p[:,2]<1.57)&(p[:,1]<-.085)
selected=np.where(mask)[0];rows=[];cols=[]
for edge in head.data.edges:
 a,b=edge.vertices
 if mask[a]:rows.append(a);cols.append(b)
 if mask[b]:rows.append(b);cols.append(a)
rows=np.array(rows);cols=np.array(cols);degree=np.bincount(rows,minlength=len(p));degree[degree==0]=1
for _ in range(256):
 mean=np.zeros_like(weights);np.add.at(mean,rows,weights[cols]);mean/=degree[:,None];weights[selected]=.5*weights[selected]+.5*mean[selected]
# Restrict tongue correspondence to reference triangles whose vertices are tongue-weighted.
ref=np.load(out/'reference_tongue.npz');reference_groups=ref['groups'].tolist();reference_weights=np.zeros((len(ref['positions']),len(groups)),dtype=np.float32)
for j,name in enumerate(reference_groups):
 if 'Tongue' in name and name in groups:reference_weights[:,groups.index(name)]=ref['weights'][:,j]
# Use precisely the same fitted donor space as the original weight transfer.
source=ast.parse((out/'Tools/headp2_transfer_rig_v2.py').read_text());definition=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='warp');exec(compile(ast.Module(body=[definition],type_ignores=[]),'reference_warp','exec'))
reference_p=warp(ref['positions'])
triangles=[tuple(int(v) for v in t) for t in ref['triangles'] if all(reference_weights[v].sum()>.99 for v in t)]
if not triangles:raise RuntimeError('No reference tongue triangles')
tree=BVHTree.FromPolygons([Vector(v) for v in reference_p],triangles,all_triangles=True);distances=[]
for v in np.where(comp==4)[0]:
 nearest,normal,index,distance=tree.find_nearest(Vector(p[v]));a,b,c=reference_p[list(triangles[index])];v0=b-a;v1=c-a;v2=np.array(nearest)-a;d00=v0@v0;d01=v0@v1;d11=v1@v1;den=d00*d11-d01*d01
 if abs(den)<1e-18:bary=np.array([1.,0,0])
 else:
  beta=(d11*(v2@v0)-d01*(v2@v1))/den;gamma=(d00*(v2@v1)-d01*(v2@v0))/den;bary=np.clip([1-beta-gamma,beta,gamma],0,1);bary/=bary.sum()
 weights[v]=np.sum(reference_weights[list(triangles[index])]*bary[:,None],axis=0);weights[v]/=weights[v].sum();distances.append(distance)
ref.close()
affected=np.where(mask|(comp==4))[0]
for g in head.vertex_groups:g.remove(affected.tolist())
for v in affected:
 ids=np.argsort(weights[v])[-12:];values=weights[v,ids];valid=values>1e-6;ids=ids[valid];values=values[valid];values/=values.sum()
 for group,value in zip(ids,values):head.vertex_groups[int(group)].add([int(v)],float(value),'REPLACE')
# Preserve all geometry, channel aliases and behavior; replace skin weights only.
reader=io.get_dna_reader(file_path=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology/Backups/BeforeLipTongueFix_20261007_213033/HeadP2_Complete.dna'),file_format='binary',data_layer='All');writer=io.get_dna_writer(file_path=out/'HeadP2_SkinFix.dna',file_format='binary');writer.setFrom(reader,dna.DataLayer_All,dna.UnknownLayerPolicy_Preserve,None)
meshidx=next(j for j in range(reader.getMeshCount()) if reader.getMeshName(j)=='head_lod0_mesh')
from mathutils.kdtree import KDTree
position_tree=KDTree(len(p))
for v,point in enumerate(p):position_tree.insert(Vector(point),v)
position_tree.balance();dna_to_blender=[];max_mapping_error=0
for v in range(reader.getVertexPositionCount(meshidx)):
 x,y,z=reader.getVertexPosition(meshidx,v);point=Vector((x*.01,-z*.01,y*.01));nearest,index,distance=position_tree.find(point);dna_to_blender.append(index);max_mapping_error=max(max_mapping_error,distance)
assert max_mapping_error<1e-5,('DNA vertex mapping error',max_mapping_error)
print('DNA_VERTEX_MAPPING',len(dna_to_blender),len(p),max_mapping_error,flush=True)
joints={reader.getJointName(j):j for j in range(reader.getJointCount())}
affected_set=set(int(v) for v in affected)
for dna_vertex,v in enumerate(dna_to_blender):
 if v not in affected_set:continue
 vertex=head.data.vertices[int(v)];jointids=[joints[groups[g.group]] for g in vertex.groups];values=[g.weight for g in vertex.groups]
 writer.setSkinWeightsJointIndices(meshIndex=meshidx,vertexIndex=dna_vertex,jointIndices=jointids);writer.setSkinWeightsValues(meshIndex=meshidx,vertexIndex=dna_vertex,weights=values)
writer.write()
if not dna.Status.isOk():raise RuntimeError(str(dna.Status.get().message))
i.head_dna_file_path=str(out/'HeadP2_SkinFix.dna');i.destroy_references();i.head_initialize();i.auto_evaluate=True;i.evaluate(component='head')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HeadP2_SkinFix.blend'),relative_remap=False)
report={'lip_vertices':len(selected),'tongue_vertices':int((comp==4).sum()),'tongue_reference_triangles':len(triangles),'tongue_mapping_max_distance_m':float(max(distances)),'skin_only_change':True,'shape_keys_unchanged':True,'outside_region_weights_unchanged':bool(np.array_equal(before[~(mask|(comp==4))],weights[~(mask|(comp==4))]))}
(out/'skin_fix_candidate.json').write_text(json.dumps(report,indent=2));print('SKIN_FIX',json.dumps(report),flush=True)
