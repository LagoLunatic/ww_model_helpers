#!/usr/bin/python3.8

import sys
import os
from io import BytesIO
from subprocess import call
from collections import OrderedDict
from PIL import Image
import re
import json
import glob

from model_helpers_paths import WWRANDO_PATH, SUPERBMD_PATH

sys.path.insert(0, WWRANDO_PATH)
from fs_helpers import *
from wwlib.rarc import RARC
from wwlib.texture_utils import *
from wwlib.bti import *
from wwlib.j3d import ColorAnimation, AnimationTrack, AnimationKeyframe, LoopMode, TangentType

class ModelConversionError(Exception):
  pass

def convert_to_bdl(base_folder, file_base_name):
  in_dae_path      = os.path.join(base_folder, file_base_name + ".dae")
  out_bdl_path     = os.path.join(base_folder, file_base_name + ".bdl")
  tex_headers_path = os.path.join(base_folder, "tex_headers.json")
  materials_path   = os.path.join(base_folder, "materials.json")
  
  print("Converting %s to BDL" % in_dae_path)
  
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
  
  if os.path.isfile(out_bdl_path):
    os.remove(out_bdl_path)
  
  command = [
    SUPERBMD_PATH,
    "-i", in_dae_path,
    "-o", out_bdl_path,
    "-x", tex_headers_path,
    "-m", materials_path,
    "-t", "all",
    "--bdl",
  ]
  
  result = call(command)
  
  if result != 0:
    input()
    sys.exit(1)
  
  return out_bdl_path

def unpack_sections(bdl_path):
  with open(bdl_path, "rb") as f:
    data = BytesIO(f.read())
  
  return unpack_sections_by_data(data)
  
def unpack_sections_by_data(data):
  bdl_size = data_len(data)
  
  sections = OrderedDict()
  
  sections["header"] = BytesIO(read_bytes(data, 0, 0x20))
  
  offset = 0x20
  while offset < bdl_size:
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

def copy_original_sections(out_bdl_path, orig_bdl_path, sections_to_copy):
  sections = unpack_sections(out_bdl_path)
  orig_sections = unpack_sections(orig_bdl_path)
  
  for section_magic in sections_to_copy:
    sections[section_magic] = orig_sections[section_magic]
  
  data = pack_sections(sections)
  
  size = data_len(data)
  write_u32(data, 8, size)
  
  with open(out_bdl_path, "wb") as f:
    data.seek(0)
    f.write(data.read())
  
  return data



def convert_all_player_models(orig_link_folder, custom_player_folder, repack_hands_model=False, rarc_name="Link.arc", no_skip_unchanged=False):
  orig_link_arc_path = os.path.join(orig_link_folder, rarc_name)
  with open(orig_link_arc_path, "rb") as f:
    rarc_data = BytesIO(f.read())
  link_arc = RARC(rarc_data)
  
  
  all_model_basenames = []
  all_texture_basenames = []
  all_bone_anim_basenames = []
  all_tev_anim_basenames = []
  all_tex_anim_basenames = []
  all_btp_anim_basenames = []
  all_bas_anim_basenames = []
  all_bpk_anim_basenames = []
  for file_entry in link_arc.file_entries:
    if file_entry.is_dir:
      continue
    basename, file_ext = os.path.splitext(file_entry.name)
    if file_ext == ".bdl":
      all_model_basenames.append(basename)
    if file_ext == ".bti":
      all_texture_basenames.append(basename)
    if file_ext == ".bck":
      all_bone_anim_basenames.append(basename)
    if file_ext == ".brk":
      all_tev_anim_basenames.append(basename)
    if file_ext == ".btk":
      all_tex_anim_basenames.append(basename)
    if file_ext == ".btp":
      all_btp_anim_basenames.append(basename)
    if file_ext == ".bas":
      all_bas_anim_basenames.append(basename)
    if file_ext == ".bpk":
      all_bpk_anim_basenames.append(basename)
  
  
  found_any_files_to_modify = False
  
  for model_basename in all_model_basenames:
    if model_basename == "hands" and not repack_hands_model:
      continue
    
    new_model_folder = os.path.join(custom_player_folder, model_basename)
    if os.path.isdir(new_model_folder):
      out_bdl_path = os.path.join(new_model_folder, model_basename + ".bdl")
      
      found_any_files_to_modify = True
      
      should_rebuild_bdl = False
      if os.path.isfile(out_bdl_path) and not no_skip_unchanged:
        last_compile_time = os.path.getmtime(out_bdl_path)
        
        relevant_file_exts = ["dae", "png", "json"]
        for file_ext in relevant_file_exts:
          relevant_file_paths = glob.glob(new_model_folder + "/*." + file_ext)
          for relevant_file_path in relevant_file_paths:
            if os.path.getmtime(relevant_file_path) > last_compile_time:
              should_rebuild_bdl = True
              break
          if should_rebuild_bdl:
            break
      else:
        should_rebuild_bdl = True
      
      if should_rebuild_bdl:
        convert_to_bdl(new_model_folder, model_basename)
      else:
        print("Skipping %s" % model_basename)
      
      orig_bdl_path = os.path.join(orig_link_folder, model_basename, model_basename + ".bdl")
      
      sections_to_copy = []
      if rarc_name.lower() == "Link.arc".lower() and model_basename in ["cl"]:
        # Link needs his original INF1/JNT1 to not crash the game.
        sections_to_copy.append("INF1")
        sections_to_copy.append("JNT1")
      if rarc_name.lower() == "Ship.arc".lower() and model_basename in ["vfncn", "vfncr"]:
        # The boat's cannon and crane need their original JNT1 or they get rotated 90 degrees.
        sections_to_copy.append("JNT1")
      
      link_arc.get_file_entry(model_basename + ".bdl").data = copy_original_sections(out_bdl_path, orig_bdl_path, sections_to_copy)
  
  for texture_basename in all_texture_basenames:
    # Create texture BTI from PNG
    texture_bti_path = os.path.join(custom_player_folder, texture_basename + ".bti")
    texture_png_path = os.path.join(custom_player_folder, texture_basename + ".png")
    
    if os.path.isfile(texture_png_path):
      found_any_files_to_modify = True
      
      print("Converting %s from PNG to BTI" % texture_basename)
      
      image = Image.open(texture_png_path)
      texture = link_arc.get_file(texture_basename + ".bti")
      
      tex_header_json_path = os.path.join(custom_player_folder, texture_basename + "_tex_header.json")
      if os.path.isfile(tex_header_json_path):
        with open(tex_header_json_path) as f:
          tex_header = json.load(f)
        
        if "Format" in tex_header:
          texture.image_format = ImageFormat[tex_header["Format"]]
        if "PaletteFormat" in tex_header:
          texture.palette_format = PaletteFormat[tex_header["PaletteFormat"]]
        if "WrapS" in tex_header:
          texture.wrap_s = WrapMode[tex_header["WrapS"]]
        if "WrapT" in tex_header:
          texture.wrap_t = WrapMode[tex_header["WrapT"]]
        if "MagFilter" in tex_header:
          texture.mag_filter = FilterMode[tex_header["MagFilter"]]
        if "MinFilter" in tex_header:
          texture.min_filter = FilterMode[tex_header["MinFilter"]]
        if "AlphaSetting" in tex_header:
          texture.alpha_setting = tex_header["AlphaSetting"]
        if "LodBias" in tex_header:
          texture.lod_bias = tex_header["LodBias"]
        if "unknown2" in tex_header:
          texture.min_lod = (tex_header["unknown2"] & 0xFF00) >> 8
          texture.max_lod = (tex_header["unknown2"] & 0x00FF)
        if "MinLOD" in tex_header:
          texture.min_lod = tex_header["MinLOD"]
        if "MaxLOD" in tex_header:
          texture.max_lod = tex_header["MaxLOD"]
        if "unknown3" in tex_header:
          texture.unknown_3 = tex_header["unknown3"]
      
      texture.replace_image(image)
      texture.save_changes()
      with open(texture_bti_path, "wb") as f:
        texture.file_entry.data.seek(0)
        f.write(texture.file_entry.data.read())
    
    # Import texture BTI
    if os.path.isfile(texture_bti_path):
      found_any_files_to_modify = True
      
      with open(texture_bti_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(texture_basename + ".bti").data = data
  
  if not repack_hands_model:
    # Import hands texture
    hands_tex_png = os.path.join(custom_player_folder, "hands", "handsS3TC.png")
    if os.path.isfile(hands_tex_png) and link_arc.get_file("hands.bdl") is not None:
      found_any_files_to_modify = True
      
      image = Image.open(hands_tex_png)
      hands_model = link_arc.get_file("hands.bdl")
      textures = hands_model.tex1.textures_by_name["handsS3TC"]
      for texture in textures:
        texture.replace_image(image)
      hands_model.save_changes()
      link_arc.get_file_entry("hands.bdl").data = hands_model.file_entry.data
  
  
  # Repack animations.
  for anim_basename in all_bone_anim_basenames:
    anim_path = os.path.join(custom_player_folder, "#Bone animations", anim_basename + ".bck")
    if os.path.isfile(anim_path):
      found_any_files_to_modify = True
      
      with open(anim_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(anim_basename + ".bck").data = data
      
  for anim_basename in all_tev_anim_basenames:
    anim_brk_path = os.path.join(custom_player_folder, "#TEV register animations", anim_basename + ".brk")
    anim_json_path = os.path.join(custom_player_folder, "#TEV register animations", anim_basename + ".json")
    
    if os.path.isfile(anim_json_path):
      found_any_files_to_modify = True
      
      print("Converting %s from JSON to BRK" % anim_basename)
      
      brk = link_arc.get_file(anim_basename + ".brk")
      load_brk_from_json(brk, anim_json_path)
      
      brk.save_changes()
      with open(anim_brk_path, "wb") as f:
        f.write(read_all_bytes(brk.file_entry.data))
    
    if os.path.isfile(anim_brk_path):
      found_any_files_to_modify = True
      
      with open(anim_brk_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(anim_basename + ".brk").data = data
  
  for anim_basename in all_tex_anim_basenames:
    anim_path = os.path.join(custom_player_folder, "#Texture animations", anim_basename + ".btk")
    if os.path.isfile(anim_path):
      found_any_files_to_modify = True
      
      with open(anim_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(anim_basename + ".btk").data = data
  
  for anim_basename in all_btp_anim_basenames:
    anim_path = os.path.join(custom_player_folder, "#Texture swap animations", anim_basename + ".btp")
    if os.path.isfile(anim_path):
      found_any_files_to_modify = True
      
      with open(anim_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(anim_basename + ".btp").data = data
  
  for anim_basename in all_bas_anim_basenames:
    anim_path = os.path.join(custom_player_folder, "#Sound effect animations", anim_basename + ".bas")
    if os.path.isfile(anim_path):
      found_any_files_to_modify = True
      
      with open(anim_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(anim_basename + ".bas").data = data
  
  for anim_basename in all_bpk_anim_basenames:
    anim_path = os.path.join(custom_player_folder, "#Color animations", anim_basename + ".bpk")
    if os.path.isfile(anim_path):
      found_any_files_to_modify = True
      
      with open(anim_path, "rb") as f:
        data = BytesIO(f.read())
        link_arc.get_file_entry(anim_basename + ".bpk").data = data
  
  
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
  link_arc_out_path = os.path.join(custom_player_folder, rarc_name)
  with open(link_arc_out_path, "wb") as f:
    link_arc.data.seek(0)
    f.write(link_arc.data.read())
  
  if not found_any_files_to_modify:
    print("No models, textures, or animations to modify found. Repacked RARC with no changes.")

def load_brk_from_json(brk, input_json_path):
  trk1 = brk.trk1
  
  with open(input_json_path) as f:
    json_dict = json.load(f)
  
  trk1.loop_mode = LoopMode[json_dict["LoopMode"]]
  trk1.duration = json_dict["Duration"]
  reg_anims_json = json_dict["RegisterAnimations"]
  konst_anims_json = json_dict["KonstantAnimations"]
  trk1.mat_name_to_reg_anims.clear()
  trk1.mat_name_to_konst_anims.clear()
  
  for anims_json, anims_dict in [(reg_anims_json, trk1.mat_name_to_reg_anims), (konst_anims_json, trk1.mat_name_to_konst_anims)]:
    for mat_name, mat_anims_json in anims_json.items():
      if mat_name in anims_dict:
        raise Exception("Duplicate material name in BRK: \"%s\"" % mat_name)
      
      anims_dict[mat_name] = []
      for anim_json in mat_anims_json:
        anim = ColorAnimation()
        anim.color_id = anim_json["ColorID"]
        anims_dict[mat_name].append(anim)
        
        for channel in ["R", "G", "B", "A"]:
          track_json = anim_json[channel]
          
          anim_track = AnimationTrack()
          setattr(anim, channel.lower(), anim_track)
          anim_track.tangent_type = TangentType[track_json["TangentType"]]
          
          anim_track.keyframes = []
          for keyframe_json in track_json["KeyFrames"]:
            time = keyframe_json["Time"]
            value = keyframe_json["Value"]
            tangent_in = keyframe_json["TangentIn"]
            tangent_out = keyframe_json["TangentOut"]
            keyframe = AnimationKeyframe(time, value, tangent_in, tangent_out)
            anim_track.keyframes.append(keyframe)

if __name__ == "__main__":
  args_valid = False
  repack_hands = False
  rarc_name = None
  no_skip_unchanged = False
  if len(sys.argv) >= 5 and sys.argv[1] in ["-link", "-clean"] and sys.argv[3] == "-custom":
    args_valid = True
  
  extra_args = sys.argv[5:]
  
  if "-repackhands" in extra_args:
    repack_hands = True
    extra_args.remove("-repackhands")
  
  if "-rarcname" in extra_args:
    rarcname_index = extra_args.index("-rarcname")
    if rarcname_index+1 >= len(extra_args):
      args_valid = False
    else:
      rarc_name = extra_args.pop(rarcname_index+1)
      extra_args.remove("-rarcname")
  
  if "-noskipunchanged" in extra_args:
    no_skip_unchanged = True
    extra_args.remove("-noskipunchanged")
  
  if extra_args:
    # Invalid extra args
    args_valid = False
  
  if not args_valid:
    print("The format for running pack_models is as follows:")
    print("  pack_models -clean \"Path/To/Clean/Model/Folder\" -custom \"Path/To/Custom/Model/Folder\"")
    print("Also, the following optional arguments can included at the end:")
    print("   -repackhands       Use this if you want to modify the hands.bdl model and not just its texture.")
    print("   -rarcname          Use this followed by the filename of the RARC if you want to manually specify what RARC name to look for (e.g. 'Link.arc'). Only needs to be specified if there are multiple .arc files in the clean folder.")
    print("   -noskipunchanged   Use this if you want to recompile all models, even unchanged ones. Without this option specified, models that haven't been changed since they were last compiled will simply have their most recent compiled version packed, in order to save time.")
    sys.exit(1)
  
  orig_link_folder = sys.argv[2]
  if not os.path.isdir(orig_link_folder):
    print("Clean link folder does not exist: %s" % orig_link_folder)
    sys.exit(1)
  
  custom_player_folder = sys.argv[4]
  if not os.path.isdir(custom_player_folder):
    print("Custom player folder does not exist: %s" % custom_player_folder)
    sys.exit(1)
  
  if not os.path.isfile(SUPERBMD_PATH):
    print("SuperBMD not found. SuperBMD.exe must be located in the SuperBMD folder.")
    sys.exit(1)
  
  if rarc_name is None:
    found_rarcs = []
    for filename in os.listdir(orig_link_folder):
      file_path = os.path.join(orig_link_folder, filename)
      if os.path.isfile(file_path) and os.path.splitext(filename)[1] == ".arc":
        found_rarcs.append(filename)
    if len(found_rarcs) == 1:
      rarc_name = found_rarcs[0]
    elif len(found_rarcs) > 1:
      print("Multiple .arc files found in the clean folder. You must specify which one to use with -rarcname.")
      sys.exit(1)
    else:
      print("No .arc files found in the clean folder.")
      sys.exit(1)
  
  try:
    convert_all_player_models(
      orig_link_folder, custom_player_folder,
      repack_hands_model=repack_hands, rarc_name=rarc_name, no_skip_unchanged=no_skip_unchanged
    )
  except ModelConversionError as e:
    print(e)
    sys.exit(1)
