
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

# Rig the casual hair mesh to the main cl.bdl skeleton, instead of the casual hair's own skeleton, so that it moves with the head when the head is posed.
skeleton_root = scene.objects["skeleton_root"]
casual_hair_mesh = bpy.data.objects[casual_hair_model_mesh_name + ".001"]
casual_hair_mesh.modifiers["Armature"].object = skeleton_root
casual_hair_mesh.vertex_groups["cl_katsura"].name = "head_jnt"

# Finally translate and rotate the casual hair mesh so that it's not down by the player's feet.
bpy.ops.object.mode_set(mode="EDIT")
armature = bpy.data.objects["skeleton_root"]
head_bone = armature.data.edit_bones["head_jnt"]
casual_hair_mesh.location = head_bone.tail # Will be (0, 83, -0.5) if the head bone has not been moved from vanilla cl.bdl
casual_hair_mesh.rotation_mode = "XYZ"
casual_hair_mesh.rotation_euler.rotate_axis("X", math.radians(90.0))
casual_hair_mesh.rotation_euler.rotate_axis("Y", math.radians(90.0))
