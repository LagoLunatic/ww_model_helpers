
# This Blender Python script automatically removes all doubled up vertices from meshes.
# If you want this script to only remove doubles from *some* objects, simply select the objects you want to be ignored and press H to hide them. Then run the script to remove doubles for the objects that are still visible. Finally press Alt+H to unhide the ignored objects.

import bpy, bpy_types, bmesh

for obj in bpy.context.scene.objects:
  if obj.data.__class__ == bpy_types.Mesh:
    if obj.hide_get():
      # Ignore hidden objects. This is so the user can choose which objects to not remove doubles on by hiding them.
      continue
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.clear()
