import bpy,importlib,addon_utils,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
u=importlib.import_module(module+'.utilities');io=importlib.import_module(module+'.dna_io')
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'Head_P2_Rig_Candidate_v3.blend'))
i=u.get_active_rig_instance();i.head_initialize();i.auto_evaluate=False;head=i.head_mesh
p=np.array([v.co[:] for v in head.data.vertices],dtype=np.float32);components=np.array([v.value for v in head.data.attributes['p2_source_component'].data])
mask=(np.abs(p[:,0])>.009)&(np.abs(p[:,0])<.065)&(p[:,2]>1.598)&(p[:,2]<1.647)&(p[:,1]<-.079)&np.isin(components,[0,5]);affected=np.where(mask)[0]
neighbors={int(v):[] for v in affected}
for e in head.data.edges:
 a,b=e.vertices
 if a in neighbors:neighbors[a].append(b)
 if b in neighbors:neighbors[b].append(a)
# The detached authored eyelid strip follows the adjacent facial skin without welding UV seams.
tree=KDTree(int((components==0).sum()))
for v in np.where(components==0)[0]:tree.insert(Vector(p[v]),int(v))
tree.balance()
for v in np.where(components==5)[0]:
 if v in neighbors:neighbors[v].extend(index for co,index,dist in tree.find_n(Vector(p[v]),3))
rows=[];cols=[]
for v,items in neighbors.items():
 for other in items:rows.append(v);cols.append(other)
rows=np.array(rows);cols=np.array(cols);degree=np.bincount(rows,minlength=len(p)).astype(np.float32);degree[degree==0]=1
weights=np.zeros((len(p),len(head.vertex_groups)),dtype=np.float32)
for v in head.data.vertices:
 for g in v.groups:weights[v.index,g.group]=g.weight
for _ in range(3):
 mean=np.zeros_like(weights);np.add.at(mean,rows,weights[cols]);mean/=degree[:,None];weights[affected]=weights[affected]*.6+mean[affected]*.4
for group in head.vertex_groups:group.remove(affected.tolist())
for v in affected:
 indices=np.argsort(weights[v])[-12:];values=weights[v,indices];values/=values.sum()
 for group,value in zip(indices,values):
  if value>1e-6:head.vertex_groups[int(group)].add([int(v)],float(value),'REPLACE')
for key in list(head.data.shape_keys.key_blocks)[1:]:
 flat=np.empty(len(p)*3,dtype=np.float32);key.data.foreach_get('co',flat);delta=flat.reshape(-1,3)-p
 for _ in range(2):
  mean=np.zeros_like(delta);np.add.at(mean,rows,delta[cols]);mean/=degree[:,None];delta[affected]=delta[affected]*.65+mean[affected]*.35
 key.data.foreach_set('co',(p+delta).ravel())
i.output.folder_path=str(out);i.output.method='overwrite'
result=io.DNAExporter(instance=i,linear_modifier=.01,file_name='HeadP2_Custom_v4.dna',component_type='head',textures=False,vertex_colors=False,seam_follower=None).run()
if not result[0]:raise RuntimeError(str(result[:3]))
i.head_dna_file_path=str(out/'HeadP2_Custom_v4.dna');i.destroy_references();i.head_initialize();i.auto_evaluate=True;i.evaluate(component='head')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Head_P2_Rig_Candidate_v4.blend'),relative_remap=False)
print('EYELID_WEIGHTS',len(affected),flush=True)
