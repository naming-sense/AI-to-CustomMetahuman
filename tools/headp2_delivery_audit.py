import bpy,addon_utils,json,numpy as np,hashlib
from pathlib import Path
addon_utils.enable('bl_ext.api_portal_polyhammer_com.character_dna',default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');source=Path('D:/ChatGPT/Resource/Head/Tripo_P2_20261006/Head_P2.blend')
bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
head=bpy.data.objects['Ettore_head_lod0_mesh'];mesh=head.data
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.meshes=[n for n in src.meshes if n.startswith('tripo_mesh')]
original=dst.meshes[0];ids=[x.value for x in mesh.attributes['p2_source_vertex'].data];faces=[x.value for x in mesh.attributes['p2_source_face'].data]
face_match=all([ids[v] for v in p.vertices]==list(original.polygons[f].vertices) for p,f in zip(mesh.polygons,faces))
uv_match=all(tuple(mesh.uv_layers[l.name].data[a].uv)==tuple(l.data[b].uv) for l in original.uv_layers for p,f in zip(mesh.polygons,faces) for a,b in zip(p.loop_indices,original.polygons[f].loop_indices))
source_positions=np.array([original.vertices[v].co[:] for v in ids]);expected=np.column_stack((source_positions[:,1]*.25,-source_positions[:,0]*.25-.03,source_positions[:,2]*.25+1.594));base=np.array([v.co[:] for v in mesh.vertices])
weight_error=max(abs(sum(g.weight for g in v.groups)-1) for v in mesh.vertices)
morphs=set(json.loads((out/'unreal_final_morph_names.json').read_text()));missing=[]
for obj in [head,bpy.data.objects['Ettore_eyeLeft_lod0_mesh'],bpy.data.objects['Ettore_eyeRight_lod0_mesh']]:
 basis=np.array([v.co[:] for v in obj.data.shape_keys.key_blocks[0].data])
 for key in list(obj.data.shape_keys.key_blocks)[1:]:
  if key.name not in morphs:
   values=np.array([v.co[:] for v in key.data]);missing.append({'name':key.name,'max_delta_m':float(np.linalg.norm(values-basis,axis=1).max())})
report={'original_blend_sha256_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==json.loads((out/'source_fingerprint.json').read_text())['source_sha256'],'retained_face_vertex_order_exact':face_match,'retained_uv_exact':uv_match,'retained_surface_error_m':float(np.linalg.norm(base-expected,axis=1).max()),'max_weight_sum_error':weight_error,'unweighted_vertices':sum(not v.groups for v in mesh.vertices),'max_influences':max(len(v.groups) for v in mesh.vertices),'unreal_omitted_morphs':missing,'unreal_omitted_nonzero_morphs':sum(x['max_delta_m']>1e-8 for x in missing)}
(out/'delivery_surface_audit.json').write_text(json.dumps(report,indent=2));print('AUDIT',json.dumps({k:v for k,v in report.items() if k!='unreal_omitted_morphs'}),flush=True)
