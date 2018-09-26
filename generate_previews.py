
import bpy
import math
import os
from mathutils import Euler
import glob
import json
import struct

context = bpy.context
scene = context.scene

blend_file_directory = bpy.path.abspath("//")
# TODO: check what happens when you haven't saved the blend file

# Need to detect if this model is based on Link, or based on Tetra/Medli, since detecting which mesh is the hat/belt buckle is different for Tetra and Medli compared to Link.
bdl_file_path = os.path.join(blend_file_directory, "cl.bdl")
with open(bdl_file_path, "rb") as f:
  f.seek(0x24)
  inf1_section_size = struct.unpack(">I", f.read(4))[0]
  if inf1_section_size == 0x460: # Tetra or Medli
    hat_material_name = "m22ear_7_"
    belt_buckle_material_name = "m20ear_5_"
  else:
    hat_material_name = "m18ear_3_"
    belt_buckle_material_name = "m23ear_8_"

# Append the casual hair mesh.
casual_hair_model_path = os.path.abspath(os.path.join(blend_file_directory, "..", "katsura", "katsura.blend", "Object"))
casual_hair_model_mesh_name = "mesh-0"
bpy.ops.wm.append(
  directory=casual_hair_model_path + "\\", # Needs to have a trailing slash
  filename=casual_hair_model_mesh_name,
)

skeleton_root = scene.objects["skeleton_root"]
scene.objects.active = skeleton_root
bpy.ops.object.mode_set(mode="POSE")
bones = skeleton_root.pose.bones
for bone in bones:
  bone.rotation_mode = "XYZ"
bones["Lshoulder_jnt"].rotation_euler.rotate_axis("Z", math.radians(-10.0))
bones["LarmA_jnt"].rotation_euler.rotate_axis("Z", math.radians(-75.0))
bones["Rshoulder_jnt"].rotation_euler.rotate_axis("Z", math.radians(-10.0))
bones["RarmA_jnt"].rotation_euler.rotate_axis("Z", math.radians(-75.0))
bones["hatA_jnt"].rotation_euler.rotate_axis("Z", math.radians(-50.0))
bones["hatB_jnt"].rotation_euler.rotate_axis("Z", math.radians(-50.0))

casual_hair_skeleton_root = scene.objects["skeleton_root.001"]
scene.objects.active = casual_hair_skeleton_root
bones = casual_hair_skeleton_root.pose.bones
for bone in bones:
  bone.rotation_mode = "XYZ"
bones["cl_katsura"].location = (0, 83, -0.5) # TODO: Read head_jnt's position dynamically and use that here
bones["cl_katsura"].rotation_euler.rotate_axis("X", math.radians(90.0))
bones["cl_katsura"].rotation_euler.rotate_axis("Y", math.radians(90.0))
bpy.ops.object.mode_set(mode="OBJECT")

def update_objects_hidden_in_render(prefix):
  for obj in scene.objects:
    if obj.data.__class__ == bpy.types.Mesh:
      print(obj.name, obj.data.materials[0].name, hat_material_name, belt_buckle_material_name)
      if obj.data.materials[0].name == hat_material_name:
        # Hide the hat mesh in casual clothes.
        obj.hide_render = (prefix == "casual")
      elif obj.data.materials[0].name == belt_buckle_material_name:
        # Hide the belt buckle mesh in casual clothes.
        obj.hide_render = (prefix == "casual")
      elif obj.data.materials[0].texture_slots[0].texture.image.name == "katsuraS3TC.png":
        # Hide the casual hair mesh in hero clothes.
        obj.hide_render = (prefix == "hero")
      elif obj.data.materials[0].texture_slots[0].texture.image.name == "podAS3TC.png":
        # Hide the sword sheath mesh.
        obj.hide_render = True
      else:
        # Show every other mesh.
        obj.hide_render = False

update_objects_hidden_in_render("hero")

bpy.ops.object.lamp_add(
  type="POINT",
  location=(5, -120, 90),
)
lamp1 = context.object
lamp1.data.energy = 250
lamp1.data.distance = 50
lamp1.data.use_specular = False
bpy.ops.object.lamp_add(
  type="POINT",
  location=(90, 55, 90),
)
lamp2 = context.object
lamp2.data.energy = 250
lamp2.data.distance = 25
lamp2.data.use_specular = False

bpy.ops.object.camera_add(
  location=(90, -120, 90),
  rotation=(math.radians(80), math.radians(0), math.radians(36.5)),
)
# Alternate camera to give a view of the back:
#bpy.ops.object.camera_add(
#  location=(33, 146, 90),
#  rotation=(math.radians(80), math.radians(0), math.radians(167)),
#)
camera = context.object
scene.camera = camera
camera.data.clip_end = 5000.0

scene.render.resolution_x = 900
scene.render.resolution_y = 1300
scene.render.layers["RenderLayer"].use_sky = False
scene.render.use_antialiasing = False

for item in bpy.data.materials:
  item.use_shadeless = False

for material in bpy.data.materials:
  material.use_transparency = True
  material.alpha = 0.0
  for texture_slot in material.texture_slots:
    if texture_slot is None:
      continue
    texture_slot.use_map_alpha = True

# Change the texture wrapping mode of all textures based on tex_headers.json so they render correctly.
tex_headers_path = os.path.join(blend_file_directory, "tex_headers.json")
with open(tex_headers_path) as f:
  tex_headers = json.load(f)
for tex_header in tex_headers:
  tex_image_name = tex_header["Name"] + ".png"
  if tex_header["WrapS"] == "ClampToEdge":
    wrap_mode = "EXTEND"
  else:
    wrap_mode = "REPEAT"
  for tex in bpy.data.textures:
    if isinstance(tex, bpy.types.ImageTexture):
      if tex.image.name == tex_image_name:
        tex.extension = wrap_mode

# Since Blender can't display pupils in the eyes, we use the closed eyes texture so it doesn't look crepy.
bpy.data.images["eyeh.1.png"].filepath = os.path.join(blend_file_directory, "eyeh.4.png")

# Render the hero clothes preview.
preview_dir = os.path.join(blend_file_directory, "preview")
if not os.path.exists(preview_dir):
  os.mkdir(preview_dir)
scene.render.filepath = os.path.join(preview_dir, "preview_hero.png")
bpy.ops.render.render(write_still=True)

# Render the casual clothes preview.
bpy.data.images["linktexS3TC.png"].filepath = os.path.join(blend_file_directory, "..", "linktexbci4.png")
update_objects_hidden_in_render("casual")
scene.render.filepath = os.path.join(preview_dir, "preview_casual.png")
bpy.ops.render.render(write_still=True)

# Now generate the masks by replacing the model's textures with the texture masks and disabling shading.
for item in bpy.data.materials:
  item.use_shadeless = True

# Don't blur the borders between red and white on the masks with image interpolation.
for texture in bpy.data.textures:
  texture.use_interpolation = False
  texture.filter_type = "FELINE" # This filter seems to be the only one that can be made to have absolutely no antialiasing.
  texture.filter_size = 0.1

color_masks_dir = os.path.join(blend_file_directory, "color_masks")

for prefix in ["hero", "casual"]:
  color_mask_file_paths = glob.glob(os.path.join(color_masks_dir, "%s_*.png" % prefix))
  
  update_objects_hidden_in_render(prefix)
  
  for color_mask_file_path in color_mask_file_paths:
    file_basename = os.path.splitext(os.path.basename(color_mask_file_path))[0]
    assert file_basename.startswith(prefix + "_")
    curr_color_name = file_basename[len(prefix + "_"):]
    
    if curr_color_name == "Skin":
      textures_to_mask = ["mouthS3TC.1.png", "eyeh.1.png", "mayuh.1.png"]
      textures_to_not_mask = ["katsuraS3TC.png"]
    elif curr_color_name == "Hair":
      textures_to_mask = ["katsuraS3TC.png"]
      textures_to_not_mask = ["mouthS3TC.1.png", "eyeh.1.png", "mayuh.1.png"]
    else:
      textures_to_mask = []
      textures_to_not_mask = ["mouthS3TC.1.png", "eyeh.1.png", "mayuh.1.png", "katsuraS3TC.png"]
    
    # Change the textures to be completely red or white, but also preserve the original alpha channel.
    for texture_name in textures_to_mask:
      image = bpy.data.images[texture_name]
      pixels = image.pixels[:] # Convert the image's pixels to a tuple to increase performance when reading from it
      new_pixels = [] # Instead of modifying the image's pixels every loop, make a new list of pixels we edit for better performance
      for i in range(len(image.pixels)//4):
        orig_alpha = pixels[i*4+3]
        new_pixels += [1.0, 0.0, 0.0, orig_alpha]
      image.pixels[:] = new_pixels # Now update the image's actual pixels just once with our pixel list
    for texture_name in textures_to_not_mask:
      image = bpy.data.images[texture_name]
      pixels = image.pixels[:]
      new_pixels = []
      for i in range(len(image.pixels)//4):
        orig_alpha = pixels[i*4+3]
        new_pixels += [1.0, 1.0, 1.0, orig_alpha]
      image.pixels[:] = new_pixels
    
    bpy.data.images["linktexS3TC.png"].filepath = os.path.join(color_masks_dir, "%s_%s.png" % (prefix, curr_color_name))
    scene.render.filepath = os.path.join(preview_dir, "preview_%s_%s.png" % (prefix, curr_color_name))
    bpy.ops.render.render(write_still=True)
