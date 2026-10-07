import bpy,json,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'Head_P2_PreserveTopology_Work.blend'))
obj=next(o for o in bpy.data.objects if o.type=='MESH');old=obj.data
parents=list(range(len(old.vertices)))
def root(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
for e in old.edges:
 a,b=e.vertices;parents[root(a)]=root(b)
parts={}
for i in range(len(parents)):parts.setdefault(root(i),[]).append(i)
parts=sorted(parts.values(),key=len,reverse=True);part_by_vertex={v:k for k,part in enumerate(parts) for v in part}
# Contour follows the visible original eye opening in the fixed orthographic diagnostic.
contour=[(225,432),(232,421),(246,412),(263,408),(285,405),(302,410),(318,425),(330,440),(316,445),(287,447),(260,443),(238,438)]
def inside(x,y):
 result=False;j=len(contour)-1
 for k,(ax,ay) in enumerate(contour):
  bx,by=contour[j]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:result=not result
  j=k
 return result
kept=[];removed=[]
for p in old.polygons:
 center=sum((old.vertices[v].co for v in p.vertices),Vector())/len(p.vertices)
 pixel_x=400+center.y/.00115;pixel_y=500-center.z/.00115
 remove=part_by_vertex[p.vertices[0]]==3 or (center.x>.12 and inside(pixel_x,pixel_y))
 (removed if remove else kept).append(p.index)
used=sorted({v for f in kept for v in old.polygons[f].vertices});lookup={v:i for i,v in enumerate(used)}
mesh=bpy.data.meshes.new('HeadP2_EyeRepair_Surface')
mesh.from_pydata([old.vertices[v].co[:] for v in used],[],[[lookup[v] for v in old.polygons[f].vertices] for f in kept]);mesh.update()
for mat in old.materials:mesh.materials.append(mat)
for new,old_index in zip(mesh.polygons,kept):new.material_index=old.polygons[old_index].material_index;new.use_smooth=old.polygons[old_index].use_smooth
for layer in old.uv_layers:
 uv=mesh.uv_layers.new(name=layer.name)
 for new,old_index in zip(mesh.polygons,kept):
  for n,o in zip(new.loop_indices,old.polygons[old_index].loop_indices):uv.data[n].uv=layer.data[o].uv
ids=mesh.attributes.new('p2_source_vertex','INT','POINT');ids.data.foreach_set('value',used)
components=mesh.attributes.new('p2_source_component','INT','POINT');components.data.foreach_set('value',[part_by_vertex[v] for v in used])
faces=mesh.attributes.new('p2_source_face','INT','FACE');faces.data.foreach_set('value',kept)
obj.data=mesh;obj.name='HeadP2_EyeRepair_Surface'
# Keep authored coordinates on the working surface; normalize with an object transform only.
transform=Matrix.Translation((0,-.03,1.594)) @ Matrix.Rotation(-math.pi/2,4,'Z') @ Matrix.Scale(.25,4)
obj.matrix_world=transform
# Use fully separate MetaHuman eyes with their existing UVs and materials.
with bpy.data.libraries.load(str(out/'Ettore_Donor_Full.blend'),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n in ['Ettore_eyeLeft_lod0_mesh','Ettore_eyeRight_lod0_mesh']]
for eye in dst.objects:
 bpy.context.scene.collection.objects.link(eye);eye.parent=None;eye.matrix_world=Matrix.Identity(4)
 for mod in list(eye.modifiers):eye.modifiers.remove(mod)
 if eye.data.shape_keys:eye.shape_key_clear()
 positions=np.array([v.co[:] for v in eye.data.vertices]);center=(positions.min(0)+positions.max(0))/2
 side=1 if center[0]>0 else -1
 target=np.array([side*.0325,-.08525,1.6175])
 positions=(positions-center)*1.35+target
 eye.data.vertices.foreach_set('co',positions.astype(np.float32).ravel());eye.name='HeadP2_eyeLeft' if side>0 else 'HeadP2_eyeRight'
 eye.data.update()
max_error=max((mesh.vertices[lookup[v]].co-old.vertices[v].co).length for v in used)
uv_equal=all(tuple(mesh.uv_layers[l.name].data[n].uv)==tuple(l.data[o].uv) for l in old.uv_layers for new,f in zip(mesh.polygons,kept) for n,o in zip(new.loop_indices,old.polygons[f].loop_indices))
report={'status':'eye_repair_candidate_requires_visual_review','original_vertices':len(old.vertices),'surface_vertices':len(mesh.vertices),'original_faces':len(old.polygons),'retained_faces':len(kept),'removed_faces':removed,'retained_position_max_error':max_error,'retained_uv_exact':uv_equal,'separate_eyes':2,'source_vertex_attribute':'p2_source_vertex','rig_applied':False}
(out/'eye_repair_verification.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Head_P2_EyeRepair_Work.blend'),relative_remap=False)
print('REPAIR',len(removed),len(used),max_error,uv_equal,flush=True)
# Diagnostic render does not change the saved work scene.
scene=bpy.context.scene;camdata=bpy.data.cameras.new('Diagnostic');cam=bpy.data.objects.new('Diagnostic',camdata);scene.collection.objects.link(cam)
cam.location=(0,-4,1.594);cam.rotation_euler=Vector((0,1,0)).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.2875;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.65,.65,.65);scene.display.shading.show_cavity=True
scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'p2_eye_repair_front.png');bpy.ops.render.render(write_still=True)
