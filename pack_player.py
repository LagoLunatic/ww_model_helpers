
import sys
import os
from io import BytesIO
from subprocess import call
from collections import OrderedDict

sys.path.insert(0, "./wwrando")
from fs_helpers import *
from wwlib.rarc import RARC

def convert_to_bmd(base_folder, file_base_name, superbmd_folder="SuperBMD"):
  in_dae_path      = os.path.join(base_folder, file_base_name + ".dae")
  out_bdl_path     = os.path.join(base_folder, file_base_name + ".bdl")
  out_bmd_path     = os.path.join(base_folder, file_base_name + ".bmd")
  tex_headers_path = os.path.join(base_folder, "tex_headers.json")
  materials_path   = os.path.join(base_folder, "materials.json")
  
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
    exit()
  
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
  link_arc_files = OrderedDict()
  
  
  # Main body
  new_model_folder = os.path.join(custom_player_folder, "main")
  if os.path.isdir(new_model_folder):
    out_bmd, out_bdl = convert_to_bmd(new_model_folder, "cl")
    orig_bdl = os.path.join(orig_link_folder, "main", "cl.bdl")
    link_arc_files["cl.bdl"] = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
      [
        "INF1",
        "MDL3",
        "JNT1"
      ]
    )
  else:
    raise Exception("No main model folder found")
    
  # Hands (texture only, model is not changed)
  new_hands_tex1 = os.path.join(custom_player_folder, "hands tex1.bin")
  if os.path.isfile(new_hands_tex1):
    orig_bdl = os.path.join(orig_link_folder, "hands", "hands.bdl")
    hands_sections = unpack_sections(orig_bdl)
    with open(new_hands_tex1, "rb") as f:
      hands_sections["TEX1"] = BytesIO(f.read())
    link_arc_files["hands.bdl"] = pack_sections(hands_sections)
  
  # Power Bracelets
  new_model_folder = os.path.join(custom_player_folder, "power bracelets")
  if os.path.isdir(new_model_folder):
    out_bmd, out_bdl = convert_to_bmd(new_model_folder, "pring")
    orig_bdl = os.path.join(orig_link_folder, "power bracelets", "pring.bdl")
    link_arc_files["pring.bdl"] = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
      ["INF1", "MDL3"]
    )
  
  # Casual hair
  new_model_folder = os.path.join(custom_player_folder, "casual hair")
  if os.path.isdir(new_model_folder):
    out_bmd, out_bdl = convert_to_bmd(new_model_folder, "katsura")
    orig_bdl = os.path.join(orig_link_folder, "casual hair", "katsura.bdl")
    link_arc_files["katsura.bdl"] = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
      [
        "INF1",
        "MDL3"
      ],
    )
    
  ## Hero's Charm
  #new_model_folder = os.path.join(custom_player_folder, "hero's charm")
  #if os.path.isdir(new_model_folder):
  #  out_bmd, out_bdl = convert_to_bmd(new_model_folder, "yamu")
  #  orig_bdl = os.path.join(orig_link_folder, "hero's charm", "yamu.bdl")
  #  link_arc_files["yamu.bdl"] = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
  #    [
  #      "INF1",
  #      "MDL3"
  #    ],
  #  )
  #
  ## Mirror Shield light ray
  #new_model_folder = os.path.join(custom_player_folder, "mirror shield light ray")
  #if os.path.isdir(new_model_folder):
  #  out_bmd, out_bdl = convert_to_bmd(new_model_folder, "ymsls00")
  #  orig_bdl = os.path.join(orig_link_folder, "mirror shield light ray", "ymsls00.bdl")
  #  link_arc_files["ymsls00.bdl"] = convert_bmd_to_bdl(out_bmd, out_bdl, orig_bdl,
  #    [
  #      #"INF1",
  #      "MDL3"
  #    ],
  #  )
  
  # Create casual_clothes_texture.bti
  casual_tex_png = os.path.join(custom_player_folder, "casual_clothes_texture.png")
  if os.path.isfile(casual_tex_png):
    from PIL import Image
    image = Image.open(casual_tex_png)
    texture = link_arc.get_file("linktexbci4.bti")
    texture.image_format = 4
    texture.palette_format = 0
    texture.replace_image(image)
    texture.save_changes()
    casual_tex_bti = os.path.join(custom_player_folder, "casual_clothes_texture.bti")
    with open(casual_tex_bti, "wb") as f:
      texture.file_entry.seek(0)
      f.write(texture.file_entry.read())
  
  # Import casual_clothes_texture.bti
  casual_tex_bti = os.path.join(custom_player_folder, "casual_clothes_texture.bti")
  if os.path.isfile(casual_tex_bti):
    with open(casual_tex_bti, "rb") as f:
      data = BytesIO(f.read())
      link_arc_files["linktexbci4.bti"] = data
  
  
  orig_link_arc_path = os.path.join(orig_link_folder, "Link.arc")
  with open(orig_link_arc_path, "rb") as f:
    rarc_data = BytesIO(f.read())
  link_arc = RARC(rarc_data)
  
  for file_name, data in link_arc_files.items():
    file_entry = link_arc.get_file_entry(file_name)
    
    if file_name.endswith(".bdl"):
      print("File %s, orig size %X, new size %X" % (file_name, data_len(file_entry.data), data_len(data)))
      orig_sections = unpack_sections_by_data(file_entry.data)
      new_sections = unpack_sections_by_data(data)
      for section_magic, section_data in orig_sections.items():
        print("  %s, orig size %X, new size %X" % (section_magic, data_len(section_data), data_len(new_sections[section_magic])))
    
    file_entry.data = data
  
  link_arc.save_changes()
  link_arc_out_path = os.path.join(custom_player_folder, "Link.arc")
  with open(link_arc_out_path, "wb") as f:
    link_arc.data.seek(0)
    f.write(link_arc.data.read())

if __name__ == "__main__":
  if len(sys.argv) != 5 or sys.argv[1] != "-link" or sys.argv[3] != "-custom":
    print("Invalid arguments. Proper format:")
    print("python convert.py -link \"Path/To/Clean/Link/Folder\" -custom \"Path/To/Custom/Model/Folder\"")
    exit()
  orig_link_folder = sys.argv[2]
  custom_player_folder = sys.argv[4]
  if not os.path.isdir(orig_link_folder):
    print("Clean link folder does not exist: %s" % orig_link_folder)
  if not os.path.isdir(custom_player_folder):
    print("Custom player folder does not exist: %s" % custom_player_folder)
  convert_all_player_models(orig_link_folder, custom_player_folder)
