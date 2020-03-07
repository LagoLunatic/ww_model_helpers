
# This Blender Python script automatically removes all doubled up vertices from all meshes.

import bpy, bpy_types, bmesh

for obj in bpy.context.scene.objects:
  if obj.data.__class__ == bpy_types.Mesh:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.clear()
