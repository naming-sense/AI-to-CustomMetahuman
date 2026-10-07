import bpy,json
from pathlib import Path
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/Textures');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='D:/ChatGPT/Resource/Head/Tripo_P2_20261006/Head_P2.blend')
info=[]
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image:
   role=[]
   for link in node.outputs['Color'].links:role.append({'to':link.to_node.type,'socket':link.to_socket.name})
   p=out/(node.image.name+'.png');node.image.filepath_raw=str(p);node.image.file_format='PNG';node.image.save()
   info.append({'image':node.image.name,'colorspace':node.image.colorspace_settings.name,'links':role,'file':str(p)})
print(json.dumps(info),flush=True)
(out/'manifest.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
print('MESH',[(o.name,list(o.dimensions),list(o.rotation_euler)) for o in bpy.data.objects if o.type=='MESH'])
