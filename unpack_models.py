
import sys
import os
from io import BytesIO
from subprocess import call
from collections import OrderedDict
import json

sys.path.insert(0, "./wwrando")
from wwlib.rarc import RARC
from wwlib.bti import BTIFile

def extract_all_models(rarc_path, filenames):
  with open(rarc_path, "rb") as f:
    data = BytesIO(f.read())
  rarc = RARC(data)
  
  rarc_basename = os.path.splitext(os.path.basename(rarc_path))[0]
  rarc_containing_folder = os.path.dirname(rarc_path)
  base_output_folder = rarc_containing_folder
  
  invalid_filenames = []
  for filename in filenames:
    file_entry = rarc.get_file_entry(filename)
    if file_entry is None:
      print("Requested invalid file to extract: %s" % filename)
      invalid_filenames.append(filename)
  if invalid_filenames:
    sys.exit(1)
  
  for file_entry in rarc.file_entries:
    if filenames and file_entry.name not in filenames:
      continue
    if file_entry.name.endswith(".bdl") or file_entry.name.endswith(".bmd"):
      extract_model_or_texture(file_entry, base_output_folder)
    if file_entry.name.endswith(".bti"):
      extract_model_or_texture(file_entry, base_output_folder)
    if os.path.splitext(file_entry.name)[1] in [".bck", ".brk", ".btk", ".btp", ".bas", ".bpk"]:
      extract_animation(file_entry, base_output_folder)

def extract_model_or_texture(file_entry, base_output_folder):
  file_basename, file_ext = os.path.splitext(file_entry.name)
  if file_ext == ".bti":
    print("Extracting texture %s" % file_entry.name)
  else:
    print("Extracting model %s" % file_entry.name)
  
  if file_ext == ".bti":
    # Don't put textures in their own folder
    output_folder = base_output_folder
  else:
    output_folder = os.path.join(base_output_folder, file_basename)
    if not os.path.isdir(output_folder):
      os.mkdir(output_folder)
  output_file_name = os.path.join(output_folder, file_entry.name)
  
  with open(output_file_name, "wb") as f:
    file_entry.data.seek(0)
    f.write(file_entry.data.read())
  
  if file_ext == ".bti":
    output_png_name = os.path.join(output_folder, file_basename + ".png")
    bti = BTIFile(file_entry)
    bti.render().save(output_png_name)
    
    output_json_name = os.path.join(output_folder, file_basename + "_tex_header.json")
    header = OrderedDict()
    header["Format"] = bti.image_format.name
    header["PaletteFormat"] = bti.palette_format.name
    header["WrapS"] = bti.wrap_s.name
    header["WrapT"] = bti.wrap_t.name
    header["MagFilter"] = bti.mag_filter.name
    header["MinFilter"] = bti.min_filter.name
    header["AlphaSetting"] = bti.alpha_setting
    header["LodBias"] = bti.lod_bias
    header["unknown2"] = bti.unknown_2
    header["unknown3"] = bti.unknown_3
    with open(output_json_name, "w") as f:
      json.dump(header, f, indent=2)
  else:
    superbmd_folder = "SuperBMD"
    command = [
      os.path.join(superbmd_folder, "SuperBMD.exe"),
      "-i", output_file_name,
    ]
    
    result = call(command)
    
    if result != 0:
      input()
      sys.exit(1)

def extract_animation(file_entry, base_output_folder):
  print("Extracting animation %s" % file_entry.name)
  
  file_basename, file_ext = os.path.splitext(file_entry.name)
  if file_ext == ".bck":
    animation_type_folder_name = "#Bone animations"
  elif file_ext == ".brk":
    animation_type_folder_name = "#TEV register animations"
  elif file_ext == ".btk":
    animation_type_folder_name = "#Texture animations"
  elif file_ext == ".btp":
    animation_type_folder_name = "#Texture swap animations"
  elif file_ext == ".bas":
    animation_type_folder_name = "#Sound effect animations"
  elif file_ext == ".bpk":
    animation_type_folder_name = "#Color animations"
  
  output_folder = os.path.join(base_output_folder, animation_type_folder_name)
  if not os.path.isdir(output_folder):
    os.mkdir(output_folder)
  output_file_name = os.path.join(output_folder, file_entry.name)
  
  with open(output_file_name, "wb") as f:
    file_entry.data.seek(0)
    f.write(file_entry.data.read())

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Invalid arguments. Proper format:")
    print("  unpack_models \"Path/To/Archive.arc\"")
    print("  Or, to only extract specific files:")
    print("  unpack_models \"Path/To/Archive.arc\" [filename1] [filename2] [...]")
    sys.exit(1)
  
  rarc_path = sys.argv[1]
  if not os.path.isfile(rarc_path):
    print("Archive does not exist: %s" % rarc_path)
    sys.exit(1)
  
  filenames = sys.argv[2:]
  
  superbmd_path = os.path.join("SuperBMD", "SuperBMD.exe")
  if not os.path.isfile(superbmd_path):
    print("SuperBMD not found. SuperBMD.exe must be located in the SuperBMD folder.")
    sys.exit(1)
  
  extract_all_models(rarc_path, filenames)
