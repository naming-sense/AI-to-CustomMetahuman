"""Read Blender mesh arrays without evaluating modifiers or changing topology."""
import hashlib
import struct


def digest(values, value_type):
    result = hashlib.sha256()
    for value in values:
        result.update(struct.pack('<' + value_type, value))
    return result.hexdigest()


def fingerprint(obj):
    mesh = obj.data
    positions = mesh.shape_keys.key_blocks[0].data if mesh.shape_keys else mesh.vertices
    return {
        'vertices': len(mesh.vertices),
        'edges': len(mesh.edges),
        'polygons': len(mesh.polygons),
        'loops': len(mesh.loops),
        'basis_positions': digest((axis for vertex in positions for axis in vertex.co), 'f'),
        'edge_indices': digest((index for edge in mesh.edges for index in edge.vertices), 'I'),
        'loop_vertex_indices': digest((loop.vertex_index for loop in mesh.loops), 'I'),
        'polygon_layout': digest((value for poly in mesh.polygons
                                  for value in (poly.loop_start, poly.loop_total)), 'I'),
        'material_indices': digest((poly.material_index for poly in mesh.polygons), 'I'),
        'uv_layers': {layer.name: digest((axis for loop in layer.data for axis in loop.uv), 'f')
                      for layer in mesh.uv_layers},
    }


def require_unchanged(obj, baseline):
    current = fingerprint(obj)
    changed = [name for name in baseline if baseline[name] != current.get(name)]
    if changed:
        raise ValueError('P2 source mesh changed: ' + ', '.join(changed))
    return current
