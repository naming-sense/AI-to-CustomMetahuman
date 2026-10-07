import bpy,addon_utils,importlib,shutil,json
from pathlib import Path
m='bl_ext.api_portal_polyhammer_com.character_dna';addon_utils.enable(m,default_set=False,persistent=False)
out=Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
review=json.loads((out/'skin_fix_review.json').read_text());preservation=json.loads((out/'skin_fix_preservation.json').read_text());assert review['pass'];assert all(preservation[k] for k in ['basis','faces','uv','shapes'])
bpy.ops.wm.open_mainfile(filepath=str(out/'HeadP2_SkinFix.blend'));i=importlib.import_module(m+'.utilities').get_active_rig_instance()
shutil.copy2(out/'HeadP2_SkinFix.dna',out/'HeadP2_Complete.dna');i.head_dna_file_path=str(out/'HeadP2_Complete.dna');i.destroy_references();i.head_initialize();i.auto_evaluate=True;i.auto_evaluate_head=True;i.evaluate(component='head')
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT');i.face_board.hide_set(False);i.face_board.select_set(True);bpy.context.view_layer.objects.active=i.face_board;bpy.ops.object.mode_set(mode='POSE')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HeadP2_Rig.blend'),relative_remap=False);print('SKIN_FIX_PROMOTED',flush=True)
