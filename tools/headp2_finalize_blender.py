import bpy,importlib,addon_utils,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
u=importlib.import_module(module+'.utilities');io=importlib.import_module(module+'.dna_io')
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'Head_P2_Rig_Candidate_v4.blend'))
i=u.get_active_rig_instance();i.head_initialize();i.auto_evaluate=False;head=i.head_mesh
with bpy.data.libraries.load('D:/ChatGPT/Resource/Head/Tripo_P2_20261006/Head_P2.blend',link=False) as (src,dst):dst.meshes=[n for n in src.meshes if n.startswith('tripo_mesh')]
original=dst.meshes[0];parents=list(range(len(original.vertices)))
def root(x):
 while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
 return x
for e in original.edges:
 a,b=e.vertices;parents[root(a)]=root(b)
parts={}
for v in original.vertices:parts.setdefault(root(v.index),[]).append(v.index)
eye_part=next(set(p) for p in parts.values() if len(p)==797)
original.calc_loop_triangles();triangles=[t for t in original.loop_triangles if t.vertices[0] in eye_part]
base=np.array([v.co[:] for v in original.vertices]);tree=BVHTree.FromPolygons([Vector(v) for v in base],[list(t.vertices) for t in triangles],all_triangles=True)
for name in ['Ettore_eyeLeft_lod0_mesh','Ettore_eyeRight_lod0_mesh']:
 eye=bpy.data.objects[name];uv=eye.data.uv_layers.active;uv_by_vertex={}
 for vertex in eye.data.vertices:
  x,y,z=vertex.co;point=Vector((-(y+.03)/.25,abs(x)/.25,(z-1.594)/.25))
  nearest,normal,idx,distance=tree.find_nearest(point);tri=triangles[idx];a,b,c=base[list(tri.vertices)];v0=b-a;v1=c-a;v2=np.array(nearest)-a
  den=(v0@v0)*(v1@v1)-(v0@v1)**2
  if abs(den)<1e-18:weights=np.array([1.,0,0])
  else:
   v=((v1@v1)*(v2@v0)-(v0@v1)*(v2@v1))/den;w=((v0@v0)*(v2@v1)-(v0@v1)*(v2@v0))/den;weights=np.array([1-v-w,v,w])
  uv_by_vertex[vertex.index]=sum((np.array(original.uv_layers.active.data[k].uv)*weight for k,weight in zip(tri.loops,weights)),np.zeros(2))
 for loop in eye.data.loops:uv.data[loop.index].uv=uv_by_vertex[loop.vertex_index]
 eye.data.materials.clear();eye.data.materials.append(head.data.materials[0])
i.output.folder_path=str(out);i.output.method='overwrite'
result=io.DNAExporter(instance=i,linear_modifier=.01,file_name='HeadP2_Rig.dna',component_type='head',textures=False,vertex_colors=False,seam_follower=None).run()
if not result[0]:raise RuntimeError(str(result[:3]))
i.head_dna_file_path=str(out/'HeadP2_Rig.dna');i.destroy_references();i.head_initialize();i.auto_evaluate=True;i.evaluate(component='head')
# Save editable original quads and shape keys before exporting the engine representation.
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HeadP2_Rig_Work.blend'),relative_remap=False)
bpy.ops.object.select_all(action='DESELECT')
for obj in [head,i.head_rig,bpy.data.objects['Ettore_eyeLeft_lod0_mesh'],bpy.data.objects['Ettore_eyeRight_lod0_mesh']]:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=head
bpy.ops.export_scene.fbx(filepath=str(out/'HeadP2_Rig.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},use_mesh_modifiers=False,add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y',path_mode='AUTO')
print('BLENDER_AND_FBX_SAVED',flush=True)
