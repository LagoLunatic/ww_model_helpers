
from zipfile import ZipFile

with ZipFile("./dist/WW_Model_Helpers.zip", "w") as zip:
  zip.write("./dist/extract_models.exe", arcname="extract_models.exe")
  zip.write("./dist/pack_player.exe", arcname="pack_player.exe")
  
  zip.write("README.md")
  zip.write("generate_previews_README.md")
  zip.write("link_models_and_textures.txt")
  
  zip.write("fix_normals.py")
  zip.write("make_materials_shadeless.py")
  zip.write("generate_previews.py")
  zip.write("add_casual_hair.py")
  zip.write("enable_texture_alpha.py")
  zip.write("remove_doubles.py")
