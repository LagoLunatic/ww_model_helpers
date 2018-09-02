
# This Blender Python script automatically switches all materials in the model to Shadeless shading so that their textures display correctly within Blender.

import bpy
for item in bpy.data.materials:
  item.use_shadeless = True
