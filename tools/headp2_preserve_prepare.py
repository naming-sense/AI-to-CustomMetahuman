import bpy, json, sys, hashlib
from pathlib import Path
out = Path('D:/Work/UnrealProjects/DeadHorizon/SourceArt/Characters/HeadP2MetaHuman/PreserveTopology')
sys.path.insert(0, str(out / 'Tools'))
from mesh_fingerprint import fingerprint, require_unchanged
source = Path('D:/ChatGPT/Resource/Head/Tripo_P2_20261006/Head_P2.blend')
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
if len(objects) != 1:
    raise RuntimeError('Expected one P2 mesh')
obj = objects[0]
baseline = fingerprint(obj)
if baseline['vertices'] != 18409 or baseline['polygons'] != 19389:
    raise RuntimeError('Unexpected source topology')
manifest = {'source': str(source), 'source_sha256': source_hash, 'object': obj.name, 'mesh': baseline, 'rig_applied': False}
(out / 'source_fingerprint.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
target = out / 'Head_P2_PreserveTopology_Work.blend'
if target.exists():
    raise RuntimeError('Work file exists; refusing overwrite')
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.wm.open_mainfile(filepath=str(target))
require_unchanged(bpy.data.objects[manifest['object']], baseline)
if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
    raise RuntimeError('Original file changed')
report = {'saved_reopened_mesh_matches': True, 'source_file_unchanged': True, 'rig_applied': False, 'mesh': baseline}
(out / 'preparation_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report), flush=True)
