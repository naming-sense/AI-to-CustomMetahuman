import bpy,addon_utils,importlib,numpy as np
from pathlib import Path
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
io=importlib.import_module(module+'.dna_io');dna=importlib.import_module(module+'.bindings').dna
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
# An analytic eye atlas: white sclera, dark brown iris and black pupil.
size=1024
axis=(np.arange(size)+.5)/size-.5
x,z=np.meshgrid(axis,axis);radius=np.sqrt(x*x+z*z);angle=np.arctan2(z,x)
pixels=np.ones((size,size,4),dtype=np.float32);pixels[:,:,:3]=(.8,.78,.73)
iris=radius<.27
fibers=.65+.15*np.sin(angle*103+radius*80)+.1*np.sin(angle*61-radius*100)
for j,color in enumerate((.08,.035,.015)):pixels[:,:,j][iris]=(color*fibers)[iris]
pupil=radius<.115;pixels[:,:,:3][pupil]=(.003,.002,.002)
rim=(radius>.25)&iris;pixels[:,:,:3][rim]=(.012,.008,.004)
img=bpy.data.images.new('HeadP2_Eye_Albedo',width=size,height=size,alpha=True)
img.pixels.foreach_set(pixels.ravel());img.filepath_raw=str(out/'HeadP2_Eye_Albedo.png');img.file_format='PNG';img.save();img.pack()
mat=bpy.data.materials.new('M_HeadP2_Eye');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.22
node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=img;mat.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
reader=io.get_dna_reader(file_path=out/'HeadP2_Complete.dna',file_format='binary',data_layer='All')
writer=io.get_dna_writer(file_path=out/'HeadP2_Complete_EyeUV.dna',file_format='binary')
writer.setFrom(reader,dna.DataLayer_All,dna.UnknownLayerPolicy_Preserve,None)
for name in ['eyeLeft_lod0_mesh','eyeRight_lod0_mesh']:
 obj=bpy.data.objects['Ettore_'+name];coords=np.array([v.co[:] for v in obj.data.vertices]);center=(coords.max(axis=0)+coords.min(axis=0))/2;diameter=max(np.ptp(coords[:,0]),np.ptp(coords[:,2]))
 uv=np.column_stack(((coords[:,0]-center[0])/diameter+.5,(coords[:,2]-center[2])/diameter+.5))
 for loop in obj.data.loops:obj.data.uv_layers.active.data[loop.index].uv=uv[loop.vertex_index]
 obj.data.materials.clear();obj.data.materials.append(mat)
 idx=next(j for j in range(reader.getMeshCount()) if reader.getMeshName(j)==name)
 layouts=[reader.getVertexLayout(idx,k) for k in range(reader.getVertexLayoutCount(idx))];new_layouts=[]
 for layout in layouts:new_layouts.append([layout[0],layout[0],layout[2]])
 writer.setVertexTextureCoordinates(meshIndex=idx,textureCoordinates=uv.tolist());writer.setVertexLayouts(meshIndex=idx,layouts=new_layouts)
writer.write()
if not dna.Status.isOk():raise RuntimeError(str(dna.Status.get().message))
import os
os.replace(out/'HeadP2_Complete_EyeUV.dna',out/'HeadP2_Complete.dna')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
print('EYE_UV_AND_MATERIAL_SAVED',flush=True)
