#!/usr/bin/python3

import sys
import os
from io import BytesIO
from subprocess import call
from collections import OrderedDict
import json

from model_helpers_paths import WWRANDO_PATH, SUPERBMD_PATH

sys.path.insert(0, WWRANDO_PATH)
from wwlib.rarc import RARC
from wwlib.bti import BTIFileEntry
from wwlib.j3d import BRK

def extract_all_models(rarc_path, filenames):
  with open(rarc_path, "rb") as f:
    data = BytesIO(f.read())
  rarc = RARC()
  rarc.read(data)
  
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
    bti = BTIFileEntry(file_entry)
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
    header["MinLOD"] = bti.min_lod
    header["MaxLOD"] = bti.max_lod
    header["unknown3"] = bti.unknown_3
    with open(output_json_name, "w") as f:
      json.dump(header, f, indent=2)
  else:
    command = [
      SUPERBMD_PATH,
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
  
  if file_ext == ".brk":
    output_json_name = os.path.join(output_folder, file_basename + ".json")
    dump_brk_to_json(file_entry, output_json_name)

def dump_brk_to_json(file_entry, output_json_name):
  brk = BRK(file_entry)
  trk1 = brk.trk1
  
  json_dict = OrderedDict()
  json_dict["LoopMode"] = trk1.loop_mode.name
  json_dict["Duration"] = trk1.duration
  reg_anims_json = OrderedDict()
  konst_anims_json = OrderedDict()
  json_dict["RegisterAnimations"] = reg_anims_json
  json_dict["KonstantAnimations"] = konst_anims_json
  
  for anims_json, anims_dict in [(reg_anims_json, trk1.mat_name_to_reg_anims), (konst_anims_json, trk1.mat_name_to_konst_anims)]:
    for mat_name, anims in anims_dict.items():
      anims_json[mat_name] = []
      for anim in anims:
        anim_json = OrderedDict()
        anims_json[mat_name].append(anim_json)
        anim_json["ColorID"] = anim.color_id
        
        for channel in ["R", "G", "B", "A"]:
          anim_track = getattr(anim, channel.lower())
          
          track_json = OrderedDict()
          anim_json[channel] = track_json
          track_json["TangentType"] = anim_track.tangent_type.name
          track_json["KeyFrames"] = []
          
          for keyframe in anim_track.keyframes:
            keyframe_json = OrderedDict()
            track_json["KeyFrames"].append(keyframe_json)
            keyframe_json["Time"] = keyframe.time
            keyframe_json["Value"] = keyframe.value
            keyframe_json["TangentIn"] = keyframe.tangent_in
            keyframe_json["TangentOut"] = keyframe.tangent_out
  
  with open(output_json_name, "w") as f:
    json.dump(json_dict, f, indent=2)

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
  
  if not os.path.isfile(SUPERBMD_PATH):
    print("SuperBMD not found. SuperBMD.exe must be located in the SuperBMD folder.")
    sys.exit(1)
  
  extract_all_models(rarc_path, filenames)
