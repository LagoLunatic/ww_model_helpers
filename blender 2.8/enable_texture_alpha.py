
# This Blender Python script enables transparency for all textures.

import bpy

for material in bpy.data.materials:
  material.blend_method = "CLIP" # Enables binary alpha (alpha blending causes issues in eevee)
  
  # Link the texture's alpha output to the shader's alpha input.
  image_node = material.node_tree.nodes["Image Texture"]
  bsdf_node = material.node_tree.nodes["Principled BSDF"]
  links = material.node_tree.links
  links.new(image_node.outputs["Alpha"], bsdf_node.inputs["Alpha"])
