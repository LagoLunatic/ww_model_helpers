
# This Blender Python script automatically reads tex_headers.json and sets the wrapping mode and interpolation filter correctly for all textures.

import bpy
import os
import json

blend_file_directory = bpy.path.abspath("//")
if not blend_file_directory:
  raise Exception("Blend file is not saved. Cannot determine the proper directory.")
tex_headers_path = os.path.join(blend_file_directory, "tex_headers.json")
if not os.path.isfile(tex_headers_path):
  raise Exception("tex_headers.json was not found.")

with open(tex_headers_path) as f:
  tex_headers = json.load(f)
tex_wrap_mode_for_image_name = {}
tex_min_filter_for_image_name = {}
for tex_header in tex_headers:
  tex_image_name = tex_header["Name"] + ".png"
  if tex_header["WrapS"] == "ClampToEdge":
    wrap_mode = "EXTEND"
  else:
    wrap_mode = "REPEAT"
  tex_wrap_mode_for_image_name[tex_image_name] = wrap_mode
  
  if tex_header["MinFilter"] == "Nearest":
    tex_min_filter_for_image_name[tex_image_name] = "Closest"
  else:
    tex_min_filter_for_image_name[tex_image_name] = "Linear"

for texture in bpy.data.textures:
  if isinstance(texture, bpy.types.ImageTexture):
    # Set the texture wrapping type for the material from the tex_headers.json.
    if texture.image.name in tex_wrap_mode_for_image_name:
      texture.extension = tex_wrap_mode_for_image_name[texture.image.name]
    
    # Set the texture interpolation for the material from the tex_headers.json.
    if texture.image.name in tex_min_filter_for_image_name:
      if tex_min_filter_for_image_name[texture.image.name] == "Closest":
        texture.use_interpolation = False
        texture.filter_type = "FELINE" # This filter seems to be the only one that can be made to have absolutely no antialiasing.
        texture.filter_size = 0.1
