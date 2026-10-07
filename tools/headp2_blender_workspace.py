import bpy,addon_utils,importlib
from pathlib import Path
from mathutils import Vector
module='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(module,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
i=importlib.import_module(module+'.utilities').get_active_rig_instance();i.head_initialize();i.evaluate(component='head')
for mat in i.head_mesh.data.materials:
 if mat and mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image and node.image.name.endswith('_0'):mat.node_tree.nodes.active=node
bpy.ops.object.select_all(action='DESELECT');i.head_rig.hide_set(True);board=i.face_board;board.hide_set(False);board.select_set(True);bpy.context.view_layer.objects.active=board
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.region_3d.view_location=Vector((.20,-.02,1.55));space.region_3d.view_distance=.85;space.region_3d.view_rotation=Vector((0,1,0)).to_track_quat('-Z','Y');space.region_3d.view_perspective='ORTHO';space.shading.type='SOLID';space.shading.color_type='TEXTURE';space.overlay.show_floor=False
bpy.ops.object.mode_set(mode='POSE');bpy.ops.wm.save_as_mainfile(filepath=str(out/'HeadP2_Rig.blend'),relative_remap=False);print('WORKSPACE_SAVED',flush=True)
