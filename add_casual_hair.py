
# Run this Blender Python script in the player's main cl.blend, and it will load the casual hair katsura.blend and position it appropriately, allowing you to more quickly test if the casual hair looks good on the model itself.

import bpy
import os
import math

context = bpy.context
scene = context.scene
blend_file_directory = bpy.path.abspath("//")

scene.objects.active = scene.objects[0]
bpy.ops.object.mode_set(mode="OBJECT")

# Append the casual hair mesh.
casual_hair_model_path = os.path.join(blend_file_directory, "..", "katsura", "katsura.blend", "Object")
casual_hair_model_mesh_name = "mesh-0"
bpy.ops.wm.append(
  directory=casual_hair_model_path + "\\", # Needs to have a trailing slash
  filename=casual_hair_model_mesh_name,
)

# Pose the casual hair so it's not down by the player's feet.
skeleton_root = scene.objects["skeleton_root"]
casual_hair_skeleton_root = scene.objects["skeleton_root.001"]
scene.objects.active = casual_hair_skeleton_root
bpy.ops.object.mode_set(mode="POSE")
bones = casual_hair_skeleton_root.pose.bones
for bone in bones:
  bone.rotation_mode = "XYZ"
bones["cl_katsura"].location = (0, 83, -0.5)
bones["cl_katsura"].rotation_euler.rotate_axis("X", math.radians(90.0))
bones["cl_katsura"].rotation_euler.rotate_axis("Y", math.radians(90.0))
