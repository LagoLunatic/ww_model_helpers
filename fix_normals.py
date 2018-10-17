
# This Blender Python script automatically fixes the normals for all meshes in a model in order to get around Blender's COLLADA importer ignoring custom normals.

import bpy, bpy_types, bmesh

# First duplicate all meshes.
orig_meshes = []
new_meshes = []
for obj in bpy.context.scene.objects:
  obj.select = False
  
  if obj.data.__class__ == bpy_types.Mesh:
    if obj.hide:
      # Ignore hidden objects. This is so the user can choose which objects to not fix the normals on by hiding them.
      continue
    
    orig_meshes.append(obj)
    
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    bpy.context.scene.objects.link(new_obj)
    
    new_meshes.append(new_obj)
    new_obj.select = True

# Then join the duplicates together into one.
bpy.context.scene.objects.active = new_meshes[0]
joined_mesh = bpy.context.scene.objects.active
bpy.ops.object.join()
joined_mesh.name = "#joined"
bpy.context.scene.objects.active = joined_mesh

# Remove duplicate vertices from the joined mesh.
bm = bmesh.new()
bm.from_mesh(joined_mesh.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
bm.to_mesh(joined_mesh.data)
joined_mesh.data.update()
bm.clear()

if len(joined_mesh.data.polygons) == 0:
  print("Joined mesh has no faces, cannot transfer normals.")
else:
  # Select the original meshes as the target of data transferring the normals.
  for obj in bpy.context.scene.objects:
    if obj in orig_meshes:
      obj.select = True
      obj.data.use_auto_smooth = True
    else:
      obj.select = False
  # Set the joined mesh as the active object so it's the source of the normals.
  bpy.context.scene.objects.active = joined_mesh

  # Perform a data transfer on normals.
  bpy.ops.object.data_transfer(
    data_type = "CUSTOM_NORMAL",
    loop_mapping = "NEAREST_POLY",
  )

# Finally delete the joined mesh.
for obj in bpy.context.scene.objects:
  obj.select = False
joined_mesh.select = True
bpy.ops.object.delete()
