
import sys
import os
from io import BytesIO
from subprocess import call

sys.path.insert(0, "./wwrando")
from wwlib.rarc import RARC
from wwlib.bti import BTIFile

def extract_all_models(rarc_path):
  with open(rarc_path, "rb") as f:
    data = BytesIO(f.read())
  rarc = RARC(data)
  
  rarc_basename = os.path.splitext(os.path.basename(rarc_path))[0]
  rarc_containing_folder = os.path.dirname(rarc_path)
  base_output_folder = os.path.join(rarc_containing_folder, rarc_basename + "_extracted")
  os.mkdir(base_output_folder)
  
  for file_entry in rarc.file_entries:
    if file_entry.name.endswith(".bdl") or file_entry.name.endswith(".bmd"):
      extract_model_or_texture(file_entry, base_output_folder)
    if file_entry.name.endswith(".bti"):
      extract_model_or_texture(file_entry, base_output_folder)

def extract_model_or_texture(file_entry, base_output_folder):
  file_basename, file_ext = os.path.splitext(file_entry.name)
  if file_ext == ".bti":
    print("Extracting texture %s" % file_entry.name)
  else:
    print("Extracting model %s" % file_entry.name)
  
  output_folder = os.path.join(base_output_folder, file_basename)
  os.mkdir(output_folder)
  output_file_name = os.path.join(output_folder, file_entry.name)
  
  with open(output_file_name, "wb") as f:
    file_entry.data.seek(0)
    f.write(file_entry.data.read())
  
  if file_ext == ".bti":
    output_png_name = os.path.join(output_folder, file_basename + ".png")
    bti = BTIFile(file_entry)
    bti.render(output_png_name)
  else:
    superbmd_folder = "SuperBMD"
    command = [
      os.path.join(superbmd_folder, "SuperBMD.exe"),
      "-i", output_file_name,
    ]
    
    result = call(command)
    
    if result != 0:
      input()
      exit()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Invalid arguments. Proper format:")
    print("python extract_models.py \"Path/To/Archive.arc\"")
    exit()
  rarc_path = sys.argv[1]
  if not os.path.isfile(rarc_path):
    print("Archive does not exist: %s" % rarc_path)
  extract_all_models(rarc_path)
