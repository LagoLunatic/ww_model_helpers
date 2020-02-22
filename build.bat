
py -3.6-32 -m PyInstaller unpack_models.spec
py -3.6-32 -m PyInstaller pack_models.spec
py -3.6-32 build.py

py -3.6-64 -m PyInstaller unpack_models.spec
py -3.6-64 -m PyInstaller pack_models.spec
py -3.6-64 build.py
