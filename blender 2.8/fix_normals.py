
# This Blender Python script automatically fixes the normals for all meshes in a model in order to get around Blender's COLLADA importer ignoring custom normals.
# If you want this script to only fix normals on *some* objects, simply select the objects you want to be ignored and press H to hide them. Then run the script to fix normals for the objects that are still visible. Finally press Alt+H to unhide the ignored objects.

import bpy, bpy_types, bmesh

view_layer = bpy.context.view_layer

# First duplicate all meshes.
orig_meshes = []
new_meshes = []
orig_objects = list(bpy.context.scene.objects)
for obj in orig_objects:
  obj.select_set(False)
  
  if obj.data.__class__ == bpy_types.Mesh:
    if obj.hide_get():
      # Ignore hidden objects. This is so the user can choose which objects to not fix the normals on by hiding them.
      continue
    
    orig_meshes.append(obj)
    
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    view_layer.active_layer_collection.collection.objects.link(new_obj)
    
    new_meshes.append(new_obj)
    new_obj.select_set(True)

# Then join the duplicates together into one.
view_layer.objects.active = new_meshes[0]
joined_mesh = view_layer.objects.active
bpy.ops.object.join()
joined_mesh.name = "#joined"
view_layer.objects.active = joined_mesh

# Remove duplicate vertices from the joined mesh.
bm = bmesh.new()
bm.from_mesh(joined_mesh.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
bm.to_mesh(joined_mesh.data)
joined_mesh.data.update()
bm.clear()

if len(joined_mesh.data.polygons) == 0:
  print("Joined mesh has no faces, cannot transfer normals.")
else:
  # Select the original meshes as the target of data transferring the normals.
  for obj in bpy.context.scene.objects:
    if obj in orig_meshes:
      obj.select_set(True)
      obj.data.use_auto_smooth = True
    else:
      obj.select_set(False)
  # Set the joined mesh as the active object so it's the source of the normals.
  view_layer.objects.active = joined_mesh

  # Perform a data transfer on normals.
  bpy.ops.object.data_transfer(
    data_type = "CUSTOM_NORMAL",
    loop_mapping = "NEAREST_POLY",
  )

# Finally delete the joined mesh.
for obj in bpy.context.scene.objects:
  obj.select_set(False)
joined_mesh.select_set(True)
bpy.ops.object.delete()
