
import os
from zipfile import ZipFile

with open("version.txt", "r") as f:
  version_number = f.read().strip()

base_zip_name = "WW Model Helpers"
base_zip_name = base_zip_name + " " + version_number

import struct
if (struct.calcsize("P") * 8) == 64:
  bits_number = "_64bit"
else:
  bits_number = "_32bit"
base_zip_name += bits_number

zip_name = base_zip_name.replace(" ", "_") + ".zip"

unpack_models_exe_path = "./dist/unpack_models.exe"
if not os.path.isfile(unpack_models_exe_path):
  raise Exception("Executable not found: %s" % exe_path)
pack_models_exe_path = "./dist/pack_models.exe"
if not os.path.isfile(pack_models_exe_path):
  raise Exception("Executable not found: %s" % exe_path)

with ZipFile("./dist/" + zip_name, "w") as zip:
  zip.write(unpack_models_exe_path, arcname="unpack_models.exe")
  zip.write(pack_models_exe_path, arcname="pack_models.exe")
  
  zip.write("README.md")
  zip.write("generate_previews_README.md")
  zip.write("custom_colors_README.md")
  zip.write("material_editing_README.md")
  zip.write("link_models_and_textures.txt")
  
  zip.write("blender 2.79/fix_normals.py")
  zip.write("blender 2.79/make_materials_shadeless.py")
  zip.write("blender 2.79/generate_previews.py")
  zip.write("blender 2.79/add_casual_hair.py")
  zip.write("blender 2.79/enable_texture_alpha.py")
  zip.write("blender 2.79/remove_doubles.py")
  zip.write("blender 2.79/set_texture_wrap_and_filter.py")
  
  zip.write("blender 2.8/fix_normals.py")
  zip.write("blender 2.8/generate_previews.py")
  zip.write("blender 2.8/add_casual_hair.py")
  zip.write("blender 2.8/enable_texture_alpha.py")
  zip.write("blender 2.8/remove_doubles.py")
  zip.write("blender 2.8/set_texture_wrap_and_filter.py")
