
py -3.6-32 -m PyInstaller extract_models.spec
py -3.6-32 -m PyInstaller pack_player.spec
py -3.6-32 build.py

py -3.6-64 -m PyInstaller extract_models.spec
py -3.6-64 -m PyInstaller pack_player.spec
py -3.6-64 build.py
