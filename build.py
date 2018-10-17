
from zipfile import ZipFile

with ZipFile("./dist/WW_Model_Helpers.zip", "w") as zip:
  zip.write("./dist/extract_models.exe", arcname="extract_models.exe")
  zip.write("./dist/pack_player.exe", arcname="pack_player.exe")
  zip.write("fix_normals.py", arcname="fix_normals.py")
  zip.write("make_materials_shadeless.py", arcname="make_materials_shadeless.py")
  zip.write("README.md", arcname="README.txt")
  zip.write("generate_previews.py", arcname="generate_previews.py")
  zip.write("generate_previews_README.md", arcname="generate_previews_README.md")
