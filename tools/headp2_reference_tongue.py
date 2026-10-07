import bpy,addon_utils,numpy as np
from pathlib import Path
addon_utils.enable('bl_ext.api_portal_polyhammer_com.character_dna',default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');bpy.ops.wm.open_mainfile(filepath=str(out/'Ettore_Donor_Full.blend'))
o=bpy.data.objects['Ettore_teeth_lod0_mesh'];o.data.calc_loop_triangles();w=np.zeros((len(o.data.vertices),len(o.vertex_groups)),dtype=np.float32)
for v in o.data.vertices:
 for g in v.groups:w[v.index,g.group]=g.weight
np.savez(out/'reference_tongue.npz',positions=np.array([v.co[:] for v in o.data.vertices]),triangles=np.array([t.vertices[:] for t in o.data.loop_triangles]),weights=w,groups=np.array([g.name for g in o.vertex_groups]));print('REFERENCE_TONGUE_SAVED',flush=True)
