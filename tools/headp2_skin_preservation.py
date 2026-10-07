import bpy,addon_utils,importlib,numpy as np,json,hashlib
from pathlib import Path
m='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(m,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
def signature(filename):
 bpy.ops.wm.open_mainfile(filepath=str(out/filename));head=bpy.data.objects['Ettore_head_lod0_mesh'];mesh=head.data
 def digest(values):return hashlib.sha256(np.asarray(values).tobytes()).hexdigest()
 shape=hashlib.sha256()
 for key in mesh.shape_keys.key_blocks:
  values=np.empty(len(mesh.vertices)*3,dtype=np.float32);key.data.foreach_get('co',values);shape.update(key.name.encode());shape.update(values.tobytes())
 weights={v.index:sorted((head.vertex_groups[g.group].name,g.weight) for g in v.groups) for v in mesh.vertices}
 return {'basis':digest([v.co[:] for v in mesh.vertices]),'faces':digest([v for poly in mesh.polygons for v in poly.vertices]),'uv':digest([v.uv[:] for v in mesh.uv_layers.active.data]),'shapes':shape.hexdigest(),'weights':weights,'components':[v.value for v in mesh.attributes['p2_source_component'].data]}
a=signature('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology/Backups/BeforeLipTongueFix_20261007_213033/HeadP2_Rig.blend');b=signature('HeadP2_SkinFix.blend');changed=[v for v in a['weights'] if a['weights'][v]!=b['weights'][v]]
report={key:a[key]==b[key] for key in ['basis','faces','uv','shapes']};report['changed_vertices']=len(changed);report['changed_components']=sorted(set(b['components'][v] for v in changed));report['max_weight_sum_error']=max(abs(sum(w for _,w in row)-1) for row in b['weights'].values());report['unweighted']=sum(not row for row in b['weights'].values())
assert all(report[k] for k in ['basis','faces','uv','shapes']);assert report['changed_components']==[0,4];assert report['unweighted']==0
(out/'skin_fix_preservation.json').write_text(json.dumps(report,indent=2));print('PRESERVATION',json.dumps(report),flush=True)
