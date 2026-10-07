import bpy,json,addon_utils,importlib
from pathlib import Path
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
module='bl_ext.api_portal_polyhammer_com.character_dna'
addon_utils.enable(module,default_set=False,persistent=False)
addon=importlib.import_module(module)
print('ADDON_READY',flush=True)
source=Path('C:/Users/YOUR_USER/Documents/Megascans Library/Downloaded/UAssets/9qipkIPG/Tier0/asset_ue/MetaHumans/Ettore/SourceAssets/Ettore.dna')
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
kwargs={f'import_lod{i}':i==0 for i in range(8)}
result=bpy.ops.character_dna.import_dna(filepath=str(source),import_mesh=True,import_bones=True,import_shape_keys=True,import_vertex_groups=True,import_materials=False,import_face_board=True,include_body=False,**kwargs)
print('IMPORT_RESULT',result,flush=True)
report={'source':str(source),'objects':[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'shapes':len(o.data.shape_keys.key_blocks) if o.type=='MESH' and o.data.shape_keys else 0,'bounds':[list(o.matrix_world @ __import__('mathutils').Vector(v)) for v in o.bound_box] if o.type=='MESH' else None} for o in bpy.data.objects]}
(out/'ettore_import.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Ettore_Donor.blend'),relative_remap=False)
print('DONOR_SAVED',flush=True)
