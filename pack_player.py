
import sys
import os
from io import BytesIO
from subprocess import call
from collections import OrderedDict
from PIL import Image
import re

sys.path.insert(0, "./wwrando")
from fs_helpers import *
from wwlib.rarc import RARC

class ModelConversionError(Exception):
  pass

def convert_to_bmd(base_folder, file_base_name, superbmd_folder="SuperBMD"):
  in_dae_path      = os.path.join(base_folder, file_base_name + ".dae")
  out_bdl_path     = os.path.join(base_folder, file_base_name + ".bdl")
  out_bmd_path     = os.path.join(base_folder, file_base_name + ".bmd")
  tex_headers_path = os.path.join(base_folder, "tex_headers.json")
  materials_path   = os.path.join(base_folder, "materials.json")
  
  # Check through the .dae file to see if there are any instances of <v/>, which would cause the "Invalid contents in element "n"" error when SuperBMD tries to read the file.
  with open(in_dae_path) as f:
    dae_contents = f.read()
  matches = re.findall(
    r"<input semantic=\"WEIGHT\" source=\"#skeleton_root_([^\"]+?)-skin-weights\" offset=\"\d+\"/>\s*" + \
    r"<vcount>[^<]+</vcount>\s*" + \
    "<v/>",
    dae_contents,
    re.MULTILINE
  )
  if matches:
    raise ModelConversionError("Error: All of the vertices in the following meshes are unweighted: " + (", ".join(matches)))
  
  print("Converting %s to BMD" % in_dae_path)
  
  if os.path.isfile(out_bmd_path):
    os.remove(out_bmd_path)
  
  command = [
    os.path.join(superbmd_folder, "SuperBMD.exe"),
    "-i", in_dae_path,
    "-o", out_bmd_path,
    "-x", tex_headers_path,
    "-m", materials_path,
    "-t", "all",
  ]
  
  result = call(command)
  
  if result != 0:
    input()
    sys.exit(1)
  
  return (out_bmd_path, out_bdl_path)

def unpack_sections(bmd_path):
  with open(bmd_path, "rb") as f:
    data = BytesIO(f.read())
  
  return unpack_sections_by_data(data)
  
def unpack_sections_by_data(data):
  bmd_size = data_len(data)
  
  sections = OrderedDict()
  
  sections["header"] = BytesIO(read_bytes(data, 0, 0x20))
  
  offset = 0x20
  while offset < bmd_size:
    section_magic = read_str(data, offset, 4)
    section_size = read_u32(data, offset+4)
    sections[section_magic] = BytesIO(read_bytes(data, offset, section_size))
    
    offset += section_size
  
  return sections

def pack_sections(sections):
  data = BytesIO()
  for section_name, section_data in sections.items():
    section_data.seek(0)
    data.write(section_data.read())
  
  return data

def convert_bmd_to_bdl(out_bmd_path, out_bdl_path, orig_bdl_path, sections_to_copy):
  sections = unpack_sections(out_bmd_path)
  orig_sections = unpack_sections(orig_bdl_path)
  
  write_str(sections["header"], 4, "bdl4", 4)
  write_u32(sections["header"], 0xC, 9) # section count must be increased to 9 to include MDL3
  
  if "MDL3" not in sections_to_copy:
    raise Exception("MDL3 must be copied when converting to BDL")
  
  for section_magic in sections_to_copy:
    sections[section_magic] = orig_sections[section_magic]
  
  data = pack_sections(sections)
  
  size = data_len(data)
  write_u32(data, 8, size)
  
  with open(out_bdl_path, "wb") as f:
    data.seek(0)
    f.write(data.read())
  
  return data



def convert_all_player_models(orig_link_folder, custom_player_folder):
  orig_link_arc_path = os.path.join(orig_link_folder, "Link.arc")
  with open(orig_link_arc_path, "rb") as f:
    rarc_data = BytesIO(f.read())
  link_arc = RARC(rarc_data)
  
  
  # Main body
  new_model_folder = os.path.join(custom_player_folder, "cl")
  if os.path.isdir(new_model_folder):
    out_bmd, out_bdl = convert_to_bmd(new_model_folder, "cl")
    orig_bdl = os.path.join(orig_link_folder, "cl", "cl.bdl")
    link_arc.get_file_entry("cl.bdl").data = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
      [
        "INF1",
        "MDL3",
        "JNT1"
      ]
    )
  else:
    raise Exception("No main model (cl) folder found")
  
  accessory_model_names = [
    "pring",    # Power Bracelets
    "yamu",     # Hero's Charm
    "hyoinomi", # Hyoi Pear
    "katsura",  # Casual hair
    "swa",      # Hero's Sword blade
    "swgripa",  # Hero's Sword hilt
    
    # TODO:
    #"swms",     # Master Sword blade
    #"swgripms", # Master Sword hilt
    #"sha",      # Hero's Shield
    #"shms",     # Mirror Shield
    #"ymsls00",  # Mirror Shield light ray
  ]
  for model_basename in accessory_model_names:
    new_model_folder = os.path.join(custom_player_folder, model_basename)
    if os.path.isdir(new_model_folder):
      out_bmd, out_bdl = convert_to_bmd(new_model_folder, model_basename)
      if model_basename == "sha":
        orig_bdl = os.path.join(orig_link_folder, "shms", "shms" + ".bdl")
      else:
        orig_bdl = os.path.join(orig_link_folder, model_basename, model_basename + ".bdl")
      link_arc.get_file_entry(model_basename + ".bdl").data = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
        [
          "INF1",
          #"JNT1",
          #"SHP1",
          #"VTX1",
          #"EVP1",
          #"DRW1",
          #"MAT3",
          #"TEX1",
          "MDL3",
        ]
      )
  
  # Import hands texture
  hands_tex_png = os.path.join(custom_player_folder, "hands", "handsS3TC.png")
  if os.path.isfile(hands_tex_png):
    image = Image.open(hands_tex_png)
    hands_model = link_arc.get_file("hands.bdl")
    textures = hands_model.tex1.textures_by_name["handsS3TC"]
    for texture in textures:
      texture.replace_image(image)
    hands_model.save_changes()
    link_arc.get_file_entry("hands.bdl").data = hands_model.file_entry.data
  
  # Create casual clothes texture BTI
  casual_tex_png = os.path.join(custom_player_folder, "linktexbci4.png")
  if os.path.isfile(casual_tex_png):
    image = Image.open(casual_tex_png)
    texture = link_arc.get_file("linktexbci4.bti")
    texture.image_format = 4
    texture.palette_format = 0
    texture.replace_image(image)
    texture.save_changes()
    casual_tex_bti = os.path.join(custom_player_folder, "linktexbci4.bti")
    with open(casual_tex_bti, "wb") as f:
      texture.file_entry.data.seek(0)
      f.write(texture.file_entry.data.read())
  
  # Import casual clothes texture BTI
  casual_tex_bti = os.path.join(custom_player_folder, "linktexbci4.bti")
  if os.path.isfile(casual_tex_bti):
    with open(casual_tex_bti, "rb") as f:
      data = BytesIO(f.read())
      link_arc.get_file_entry("linktexbci4.bti").data = data
  
  # Print out changed file sizes
  with open(orig_link_arc_path, "rb") as f:
    rarc_data = BytesIO(f.read())
  orig_link_arc = RARC(rarc_data)
  for file_entry in link_arc.file_entries:
    orig_file_entry = orig_link_arc.get_file_entry(file_entry.name)
    if file_entry.is_dir:
      continue
    if data_len(orig_file_entry.data) == data_len(file_entry.data):
      continue
    print("File %s, orig size %X, new size %X" % (file_entry.name, data_len(orig_file_entry.data), data_len(file_entry.data)))
  
  link_arc.save_changes()
  link_arc_out_path = os.path.join(custom_player_folder, "Link.arc")
  with open(link_arc_out_path, "wb") as f:
    link_arc.data.seek(0)
    f.write(link_arc.data.read())

if __name__ == "__main__":
  if len(sys.argv) != 5 or sys.argv[1] != "-link" or sys.argv[3] != "-custom":
    print("Invalid arguments. Proper format:")
    print("  pack_player -link \"Path/To/Clean/Link/Folder\" -custom \"Path/To/Custom/Model/Folder\"")
    sys.exit(1)
  
  orig_link_folder = sys.argv[2]
  if not os.path.isdir(orig_link_folder):
    print("Clean link folder does not exist: %s" % orig_link_folder)
    sys.exit(1)
  
  custom_player_folder = sys.argv[4]
  if not os.path.isdir(custom_player_folder):
    print("Custom player folder does not exist: %s" % custom_player_folder)
    sys.exit(1)
  
  superbmd_path = os.path.join("SuperBMD", "SuperBMD.exe")
  if not os.path.isfile(superbmd_path):
    print("SuperBMD not found. SuperBMD.exe must be located in the SuperBMD folder.")
    sys.exit(1)
  
  try:
    convert_all_player_models(orig_link_folder, custom_player_folder)
  except ModelConversionError as e:
    print(e)
    sys.exit(1)
