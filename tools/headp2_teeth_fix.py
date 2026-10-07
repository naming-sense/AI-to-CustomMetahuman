import bpy,importlib,addon_utils,json,numpy as np
from pathlib import Path
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
u=importlib.import_module(module+'.utilities');io=importlib.import_module(module+'.dna_io')
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'Head_P2_Rig_Candidate_v2.blend'))
i=u.get_active_rig_instance();i.head_initialize();i.auto_evaluate=False;head=i.head_mesh
components=np.array([v.value for v in head.data.attributes['p2_source_component'].data]);report={}
for comp,bone in [(1,'FACIAL_C_TeethLower'),(2,'FACIAL_C_TeethUpper'),(6,'FACIAL_C_TeethUpper')]:
 indices=np.where(components==comp)[0].tolist()
 for group in head.vertex_groups:group.remove(indices)
 group=head.vertex_groups.get(bone) or head.vertex_groups.new(name=bone);group.add(indices,1,'REPLACE');report[str(comp)]={'vertices':len(indices),'bone':bone}
base=np.array([v.co[:] for v in head.data.vertices],dtype=np.float32);rigid=np.isin(components,[1,2,6])
for key in list(head.data.shape_keys.key_blocks)[1:]:
 flat=np.empty(len(base)*3,dtype=np.float32);key.data.foreach_get('co',flat);points=flat.reshape(-1,3);points[rigid]=base[rigid];key.data.foreach_set('co',points.ravel())
i.output.folder_path=str(out);i.output.method='overwrite'
result=io.DNAExporter(instance=i,linear_modifier=.01,file_name='HeadP2_Custom_v3.dna',component_type='head',textures=False,vertex_colors=False,seam_follower=None).run()
if not result[0]:raise RuntimeError(str(result[:3]))
i.head_dna_file_path=str(out/'HeadP2_Custom_v3.dna');i.destroy_references();i.head_initialize();i.auto_evaluate=True;i.evaluate(component='head')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Head_P2_Rig_Candidate_v3.blend'),relative_remap=False)
(out/'teeth_binding_fix.json').write_text(json.dumps(report,indent=2));print('TEETH_FIXED',json.dumps(report),flush=True)
