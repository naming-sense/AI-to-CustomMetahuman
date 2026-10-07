import bpy,addon_utils,importlib
from pathlib import Path
from mathutils import Matrix
m='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(m,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology');bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_Rig.blend'))
i=importlib.import_module(m+'.utilities').get_active_rig_instance();i.auto_evaluate=False;i.auto_evaluate_head=False
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
selected=[i.head_mesh,i.head_rig,bpy.data.objects['Ettore_eyeLeft_lod0_mesh'],bpy.data.objects['Ettore_eyeRight_lod0_mesh']]
for obj in selected:
 if obj.type=='MESH':obj.data.transform(Matrix.Scale(100,4),shape_keys=True)
 else:obj.data.pose_position='REST';obj.data.transform(Matrix.Scale(100,4))
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.01
bpy.ops.object.select_all(action='DESELECT')
for obj in selected:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=i.head_mesh
bpy.ops.export_scene.fbx(filepath=str(out/'HeadP2_Complete_CM.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},use_mesh_modifiers=False,add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,apply_scale_options='FBX_SCALE_UNITS',apply_unit_scale=True,axis_forward='-Z',axis_up='Y',path_mode='AUTO',colors_type='NONE')
print('CM_EXPORT_ONLY_ORIGINAL_BLEND_NOT_SAVED',flush=True)
