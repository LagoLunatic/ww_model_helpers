
# This Blender Python script enables transparency for all textures.

import bpy

for material in bpy.data.materials:
  material.use_transparency = True
  material.alpha = 0.0
  for texture_slot in material.texture_slots:
    if texture_slot is None:
      continue
    texture_slot.use_map_alpha = True
