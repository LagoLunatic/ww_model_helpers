
import bpy
import math
import os
from mathutils import Euler
import glob
import json
import struct
import tempfile
import shutil
import re
from collections import OrderedDict

context = bpy.context
scene = context.scene
world = bpy.data.worlds[0]

blend_file_directory = bpy.path.abspath("//")
if not blend_file_directory:
  raise Exception("Blend file is not saved. Cannot determine the proper directory.")
color_masks_dir = os.path.join(blend_file_directory, "color_masks")
if not os.path.isdir(color_masks_dir):
  raise Exception("color_masks directory was not found.")
preview_dir = os.path.join(blend_file_directory, "preview")
casual_clothes_tex_path = os.path.join(blend_file_directory, "..", "linktexbci4.png")
if not os.path.isfile(casual_clothes_tex_path):
  raise Exception("Casual clothes texture (linktexbci4.png) was not found.")
pupil_image_path = os.path.join(blend_file_directory, "hitomi.png")
if not os.path.isfile(pupil_image_path):
  raise Exception("Pupil texture (hitomi.png) was not found.")
bdl_file_path = os.path.join(blend_file_directory, "cl.bdl")
if not os.path.isfile(bdl_file_path):
  raise Exception("cl.bdl was not found.")
tex_headers_path = os.path.join(blend_file_directory, "tex_headers.json")
if not os.path.isfile(tex_headers_path):
  raise Exception("tex_headers.json was not found.")
model_metadata_path = os.path.join(blend_file_directory, "metadata.txt")
if not os.path.isfile(model_metadata_path):
  raise Exception("metadata.txt was not found.")
casual_hair_model_path = os.path.join(blend_file_directory, "..", "katsura", "katsura.blend")
if not os.path.isfile(casual_hair_model_path):
  raise Exception("Casual hair model (katsura.blend) was not found.")
temp_dir = tempfile.mkdtemp()

# Need to detect if this model is based on Link, or based on Tetra/Medli, since detecting which mesh is the hat/belt buckle is different for Tetra and Medli compared to Link.
with open(bdl_file_path, "rb") as f:
  f.seek(0x24)
  inf1_section_size = struct.unpack(">I", f.read(4))[0]
  if inf1_section_size == 0x460: # Tetra or Medli
    hat_material_name = "m22ear_7_"
    belt_buckle_material_name = "m20ear_5_"
  else:
    hat_material_name = "m18ear_3_"
    belt_buckle_material_name = "m23ear_8_"

scene.objects.active = scene.objects[0]
bpy.ops.object.mode_set(mode="OBJECT")

# Append the casual hair mesh.
casual_hair_model_mesh_name = "mesh-0"
bpy.ops.wm.append(
  directory=casual_hair_model_path + "\\Object\\", # Needs to have a trailing slash
  filename=casual_hair_model_mesh_name,
)

# Pose the model so it's not T-posing.
skeleton_root = scene.objects["skeleton_root"]
scene.objects.active = skeleton_root
bpy.ops.object.mode_set(mode="POSE")
bones = skeleton_root.pose.bones
for bone in bones:
  bone.rotation_mode = "XYZ"
bones["Lshoulder_jnt"].rotation_euler = (0.000000, -0.000000, -0.437075)
bones["LarmA_jnt"].rotation_euler = (0.061420, 0.112105, -0.818639)
bones["LarmB_jnt"].rotation_euler = (-0.161012, -0.485416, -0.033357)
bones["Rshoulder_jnt"].rotation_euler = (0.000000, 0.000000, -0.394006)
bones["RarmA_jnt"].rotation_euler = (-0.086200, -0.138778, -0.856716)
bones["RarmB_jnt"].rotation_euler = (0.180819, 0.423769, -0.086300)
bones["cl_podA"].rotation_euler = (0.000000, -0.000000, -0.577303)
bones["hatA_jnt"].rotation_euler = (0.000000, 0.000000, -1.159582)
bones["hatB_jnt"].rotation_euler = (0.000000, 0.000000, -0.138675)
bones["hatC_jnt"].rotation_euler = (0.000000, 0.000000, -0.315255)
bones["Lclotch_jnt"].rotation_euler = (-0.102936, 0.003428, -0.106704)
bones["LlegB_jnt"].rotation_euler = (-0.005748, -0.037766, 0.302607)
bones["Lfoot_jnt"].rotation_euler = (-0.096673, 0.326072, 0.146885)
bones["Rclotch_jnt"].rotation_euler = (0.091450, -0.012720, -0.202730)
bones["RlegB_jnt"].rotation_euler = (0.017057, 0.070484, 0.474697)
bones["Rfoot_jnt"].rotation_euler = (0.089334, -0.484198, 0.215261)

# Rig the casual hair mesh to the main cl.bdl skeleton, instead of the casual hair's own skeleton, so that it moves with the head when the head is posed.
skeleton_root = scene.objects["skeleton_root"]
casual_hair_mesh = bpy.data.objects[casual_hair_model_mesh_name + ".001"]
casual_hair_mesh.modifiers["Armature"].object = skeleton_root
casual_hair_mesh.vertex_groups["cl_katsura"].name = "head_jnt"

# Finally translate and rotate the casual hair mesh so that it's not down by the player's feet.
bpy.ops.object.mode_set(mode="EDIT")
armature = bpy.data.objects["skeleton_root"]
head_bone = armature.data.edit_bones["head_jnt"]
casual_hair_mesh.location = head_bone.tail # Will be (0, 83, -0.5) if the head bone has not been moved from vanilla cl.bdl
casual_hair_mesh.rotation_mode = "XYZ"
casual_hair_mesh.rotation_euler.rotate_axis("X", math.radians(90.0))
casual_hair_mesh.rotation_euler.rotate_axis("Y", math.radians(90.0))

bpy.ops.object.mode_set(mode="OBJECT")

orig_tex_names_for_objs = {}
for obj in scene.objects:
  if obj.data.__class__ == bpy.types.Mesh:
    orig_tex_names_for_objs[obj] = obj.data.materials[0].texture_slots[0].texture.image.name

def update_objects_hidden_in_render(prefix):
  for obj in scene.objects:
    if obj.data.__class__ == bpy.types.Mesh:
      if obj.data.materials[0].name == hat_material_name:
        # Hide the hat mesh in casual clothes.
        obj.hide_render = obj.hide = (prefix == "casual")
      elif obj.data.materials[0].name == belt_buckle_material_name:
        # Hide the belt buckle mesh in casual clothes.
        obj.hide_render = obj.hide = (prefix == "casual")
      elif orig_tex_names_for_objs[obj] == "katsuraS3TC.png":
        # Hide the casual hair mesh in hero clothes.
        obj.hide_render = obj.hide = (prefix == "hero")
      elif orig_tex_names_for_objs[obj] == "podAS3TC.png":
        # Hide the sword sheath mesh.
        obj.hide_render = obj.hide = True
      elif obj.data.materials[0].name in ["m2eyeLdamA", "m3eyeLdamB", "m5eyeRdamA", "m6eyeRdamB"]:
        # Hide the duplicate eye meshes.
        obj.hide_render = obj.hide = True
      elif obj.data.materials[0].name in ["m9mayuLdamA", "m10mayuLdamB", "m12mayuRdamA", "m13mayuRdamB"]:
        # Hide the duplicate eyebrow meshes.
        obj.hide_render = obj.hide = True
      else:
        # Show every other mesh.
        obj.hide_render = obj.hide = False

update_objects_hidden_in_render("hero")

# Set the render resolution.
# The randomizer will display it at 225x350 to the user.
# But we render it at twice that size so the randomizer can work with the non-antialiased render, and then scale it down to get antialiasing.
scene.render.resolution_x = 225*2
scene.render.resolution_y = 350*2
scene.render.resolution_percentage = 100

# Make the background transparent (for the masks).
scene.render.layers["RenderLayer"].use_sky = False

# Masks need to be binary, they won't work properly if they have antialiasing.
scene.render.use_antialiasing = False

# Add camera.
bpy.ops.object.camera_add(
  location=(105, -140, 100),
  rotation=(math.radians(80), math.radians(0), math.radians(36.5)),
)
# Alternate camera to give a view of the back:
#bpy.ops.object.camera_add(
#  location=(33, 146, 90),
#  rotation=(math.radians(80), math.radians(0), math.radians(167)),
#)
camera = context.object
scene.camera = camera
camera.data.clip_end = 5000.0

# Make materials use transparency correctly (for the masks).
for material in bpy.data.materials:
  material.use_transparency = True
  material.alpha = 0.0
  for texture_slot in material.texture_slots:
    if texture_slot is None:
      continue
    texture_slot.use_map_alpha = True

# Change the texture wrapping mode of all textures based on tex_headers.json so they render correctly (for the masks).
with open(tex_headers_path) as f:
  tex_headers = json.load(f)
tex_wrap_mode_for_image_name = {}
tex_min_filter_for_image_name = {}
for tex_header in tex_headers:
  tex_image_name = tex_header["Name"] + ".png"
  if tex_header["WrapS"] == "ClampToEdge":
    wrap_mode = "EXTEND"
  else:
    wrap_mode = "REPEAT"
  tex_wrap_mode_for_image_name[tex_image_name] = wrap_mode
  
  if tex_header["MinFilter"] == "Nearest":
    tex_min_filter_for_image_name[tex_image_name] = "Closest"
  else:
    tex_min_filter_for_image_name[tex_image_name] = "Linear"
  
  for tex in bpy.data.textures:
    if isinstance(tex, bpy.types.ImageTexture):
      if tex.image.name == tex_image_name:
        tex.extension = wrap_mode

model_metadata = {}
last_custom_colors_hash = None
with open(model_metadata_path) as f:
  for line in f.readlines():
    match = re.search(r"^(\S[^\n\r:]*): (.+)$", line)
    colors_hash_start_match = re.search(r"^(\S[^\n\r:]*):$", line)
    color_match = re.search(r"^ +(\S[^\n\r:]*): (.+)$", line)
    if match:
      key = match.group(1)
      val = match.group(2).strip()
      if val.lower() == "true":
        val = True
      elif val.lower() == "false":
        val = False
      
      model_metadata[key] = val
    elif colors_hash_start_match:
      key = colors_hash_start_match.group(1)
      if key == "hero_custom_colors" or key == "casual_custom_colors":
        in_custom_colors = True
      else:
        in_custom_colors = False
      model_metadata[key] = OrderedDict()
      last_custom_colors_hash = model_metadata[key]
    elif color_match and last_custom_colors_hash is not None:
      key = color_match.group(1)
      val = color_match.group(2).strip()
      last_custom_colors_hash[key] = val

# Increase z-index of the eye and eyebrow meshes (for the masks).
for mat_name in ["m1eyeL", "m4eyeR", "m8mayuL", "m11mayuR"]:
  mat = bpy.data.materials[mat_name]
  mat.offset_z = 1000

# Now generate the masks by replacing the model's textures with the texture masks and disabling shading.
for item in bpy.data.materials:
  item.use_shadeless = True

# Don't blur the borders between red and white on the masks with image interpolation.
for texture in bpy.data.textures:
  if isinstance(texture, bpy.types.ImageTexture):
    texture.use_interpolation = False
    texture.filter_type = "FELINE" # This filter seems to be the only one that can be made to have absolutely no antialiasing.
    texture.filter_size = 0.1

# Make a copy of all images so we can change those into the masks.
orig_images = list(bpy.data.images)
for image in orig_images:
  if len(image.pixels) == 0:
    continue
  
  temp_img_path = os.path.join(temp_dir, image.name)
  image.save_render(filepath=temp_img_path)
  mask_image = bpy.data.images.load(temp_img_path)
  mask_image.name = image.name + "_mask"
  
  for tex in bpy.data.textures:
    if isinstance(tex, bpy.types.ImageTexture):
      if tex.image == image:
        tex.image = mask_image

# Create the pupil image.
bpy.data.images.load(pupil_image_path)
hitomi_image = bpy.data.images["hitomi.png"]
hitomi_width, hitomi_height = hitomi_image.size
hitomi_pixels = hitomi_image.pixels[:] # Convert the image's pixels to a tuple to increase performance when reading from it

orig_linktexS3TC_path = bpy.data.images["linktexS3TC.png"].filepath

for prefix in ["hero", "casual"]:
  color_mask_file_paths = glob.glob(os.path.join(color_masks_dir, "%s_*.png" % prefix))
  
  update_objects_hidden_in_render(prefix)
  
  has_colored_eyebrows = model_metadata.get("has_colored_eyebrows", False)
  hands_color_name = model_metadata.get(prefix + "_hands_color_name", "Skin")
  mouth_color_name = model_metadata.get(prefix + "_mouth_color_name", "Skin")
  hitomi_color_name = model_metadata.get(prefix + "_hitomi_color_name", "Eyes")
  eyebrow_color_name = model_metadata.get(prefix + "_eyebrow_color_name", "Hair")
  casual_hair_color_name = model_metadata.get("casual_hair_color_name", "Hair")
  
  if model_metadata.get(prefix + "_custom_colors") is None:
    continue
  
  for curr_color_name, curr_color_value in model_metadata.get(prefix + "_custom_colors").items():
    textures_to_mask = []
    textures_to_not_mask = []
    textures_to_not_mask.append("linktexS3TC.png") # Will be masked later
    replaced_any_pupils_for_this_color = False
    if has_colored_eyebrows and curr_color_name == eyebrow_color_name:
      textures_to_mask.append("mayuh.1.png")
    else:
      textures_to_not_mask.append("mayuh.1.png")
    if curr_color_name == casual_hair_color_name:
      textures_to_mask.append("katsuraS3TC.png")
    else:
      textures_to_not_mask.append("katsuraS3TC.png")
    if curr_color_name == mouth_color_name:
      textures_to_mask.append("mouthS3TC.1.png")
    else:
      textures_to_not_mask.append("mouthS3TC.1.png")
    if curr_color_name == hitomi_color_name:
      replaced_any_pupils_for_this_color = True
      textures_to_mask.append("eyeh.1.png")
    else:
      textures_to_not_mask.append("eyeh.1.png")
    
    # Change the textures to be completely red or white, but also preserve the original alpha channel from the texture (not the mask).
    for texture_name in textures_to_mask + textures_to_not_mask:
      mask_image = bpy.data.images[texture_name + "_mask"]
      tex_image = bpy.data.images[texture_name]
      tex_pixels = tex_image.pixels[:] # Convert the image's pixels to a tuple to increase performance when reading from it
      new_pixels = [] # Instead of modifying the image's pixels every loop, make a new list of pixels we edit for better performance
      tex_width, tex_height = tex_image.size
      for i in range(len(mask_image.pixels)//4):
        orig_alpha = tex_pixels[i*4+3]
        r = 1.0
        g = 1.0
        b = 1.0
        
        if texture_name in textures_to_mask:
          g = 0.0
          b = 0.0
          
          if texture_name == "eyeh.1.png":
            # We only want to mask the parts of the eye where the pupil and eye whites overlap.
            orig_r = tex_pixels[i*4+0]
            orig_g = tex_pixels[i*4+1]
            orig_b = tex_pixels[i*4+2]
            
            # eyeh.1 and hitomi might not be the same resolution, so we need to map the index in eyeh.1 to the index in hitomi.
            tex_x = i % tex_width
            tex_y = i // tex_width
            x = tex_x / tex_width
            y = tex_y / tex_height
            hitomi_x = int(x * hitomi_width)
            hitomi_y = int(y * hitomi_height)
            hitomi_i = (hitomi_y*hitomi_width) + hitomi_x
            
            hitomi_r = hitomi_pixels[hitomi_i*4+0]
            hitomi_g = hitomi_pixels[hitomi_i*4+1]
            hitomi_b = hitomi_pixels[hitomi_i*4+2]
            eye_is_not_white = (orig_r <= 0.5 and orig_g <= 0.5 and orig_b <= 0.5)
            hitomi_is_white = (hitomi_r > 0.5 and hitomi_g > 0.5 and hitomi_r > 0.5)
            if eye_is_not_white or hitomi_is_white:
              g = 1.0
              b = 1.0
        
        new_pixels += [r, g, b, orig_alpha]
      mask_image.pixels[:] = new_pixels # Now update the image's actual pixels just once with our pixel list
    
    if prefix == "casual":
      bpy.data.images["linktexS3TC.png"].filepath = casual_clothes_tex_path
    else:
      bpy.data.images["linktexS3TC.png"].filepath = orig_linktexS3TC_path
    
    def load_mask_texture(texture_name, color_mask_path):
      bpy.data.images[texture_name + "_mask"].filepath = color_mask_path
      mask_image = bpy.data.images[texture_name + "_mask"]
      mask_pixels = mask_image.pixels[:]
      tex_image = bpy.data.images[texture_name]
      tex_pixels = tex_image.pixels[:]
      new_pixels = []
      for i in range(len(mask_image.pixels)//4):
        orig_alpha = tex_pixels[i*4+3]
        r = mask_pixels[i*4]
        g = mask_pixels[i*4+1]
        b = mask_pixels[i*4+2]
        
        if texture_name == "eyeh.1.png":
          # For the pupil mask, we don't want any parts of the pupil that extend outside of the whites of the eyes to be masked for the preview.
          orig_r = tex_pixels[i*4+0]
          orig_g = tex_pixels[i*4+1]
          orig_b = tex_pixels[i*4+2]
          if orig_r <= 0.5 and orig_g <= 0.5 and orig_b <= 0.5:
            r = 1.0
            g = 1.0
            b = 1.0
        
        new_pixels += [r, g, b, orig_alpha]
      mask_image.pixels[:] = new_pixels # Now update the image's actual pixels just once with our pixel list
    
    # Apply the masks to the eyes.
    color_mask_path = os.path.join(color_masks_dir, "hitomi_%s_%s.png" % (prefix, curr_color_name))
    if os.path.isfile(color_mask_path):
      replaced_any_pupils_for_this_color = True
      load_mask_texture("eyeh.1.png", color_mask_path)
    
    # Apply the masks to the main link body texture.
    color_mask_path = os.path.join(color_masks_dir, "%s_%s.png" % (prefix, curr_color_name))
    if os.path.isfile(color_mask_path):
      load_mask_texture("linktexS3TC.png", color_mask_path)
    else:
      if replaced_any_pupils_for_this_color:
        # No mask for the main body texture is allowed if this is a color for pupils. Leave the main body texture white.
        pass
      else:
        raise Exception("Failed to find color mask: %s_%s.png" % (prefix, curr_color_name))
    
    # Apply the masks to the mouth.
    color_mask_path = os.path.join(color_masks_dir, "mouths", "mouthS3TC.1_%s.png" % (curr_color_name))
    if os.path.isfile(color_mask_path):
      load_mask_texture("mouthS3TC.1.png", color_mask_path)
    
    # Render the preview mask.
    scene.render.filepath = os.path.join(preview_dir, "preview_%s_%s.png" % (prefix, curr_color_name))
    bpy.ops.render.render(write_still=True)
    
    # Now make sure the mask is binary by converting unwanted colors to pure red (e.g. pink colors where the eyes meet the skin).
    # Must save render to disk then reload as a new image to access the pixels of the render.
    render_image = bpy.data.images.load(scene.render.filepath)
    pixels = render_image.pixels[:]
    new_pixels = []
    for i in range(len(render_image.pixels)//4):
      r, g, b, a = pixels[i*4:i*4+4]
      if a < 0.5:
        new_pixels += [r, g, b, 0.0]
      elif r > 0.75 and g > 0.75 and b > 0.75:
        new_pixels += [1.0, 1.0, 1.0, 1.0]
      else:
        new_pixels += [1.0, 0.0, 0.0, 1.0]
    render_image.pixels[:] = new_pixels
    render_image.save_render(scene.render.filepath)




# Now render the actual preview images, using Cycles so we can have proper toon shading.
scene.render.engine = "CYCLES"
world.light_settings.use_ambient_occlusion = True
world.light_settings.ao_factor = 0.3
scene.cycles.film_transparent = True
scene.cycles.filter_width = 0.01 # Effectively disables antialiasing where meshes meet

# Add lighting.
for lamp_i in range(2):
  bpy.ops.object.lamp_add(
    type="SUN",
    location=(17, -82, 100),
    rotation=(math.radians(75), math.radians(15), math.radians(0)),
  )
  lamp = context.object
  lamp.data.shadow_soft_size = 0.04
  lamp.data.use_specular = False
  
  # We make a second lamp and put it on the second layer so the eyes have lighting there.
  lamp.layers = [layer_i == lamp_i for layer_i in range(len(lamp.layers))]
  if lamp_i == 1:
    lamp.hide = True # Hide the second lamp from the viewport.

# Create the Cycles materials for all objects.
done_mat_names = []
image_nodes = []
for obj in scene.objects:
  if obj.data.__class__ == bpy.types.Mesh:
    mat = obj.data.materials[0]
    tex_name = orig_tex_names_for_objs[obj]
    
    if mat.name in done_mat_names:
      continue
    done_mat_names.append(mat.name)
    
    mat.use_shadeless = False
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf_node = None
    output_node = None
    for node in mat.node_tree.nodes:
      if node.__class__ == bpy.types.ShaderNodeBsdfDiffuse:
        bsdf_node = node
      elif node.__class__ == bpy.types.ShaderNodeOutputMaterial:
        output_node = node
    if bsdf_node:
      nodes.remove(bsdf_node)
    output_node.location = (800, 400)
    
    image_node = nodes.new("ShaderNodeTexImage")
    image_node.image = bpy.data.images[tex_name]
    image_nodes.append(image_node)
    
    # Set the texture interpolation for the material from the tex_headers.json.
    if tex_name in tex_min_filter_for_image_name:
      image_node.interpolation = tex_min_filter_for_image_name[tex_name]
    
    toon_node = nodes.new("ShaderNodeBsdfToon")
    toon_node.location = (400, 400)
    
    if tex_name == "eyeh.1.png":
      # Eyes. Need transparent backgrounds and for the pupil to be overlayed on the whites of the eyes.
      mix_node = nodes.new("ShaderNodeMixShader")
      mix_node.location = (600, 200)
      transparent_node = nodes.new("ShaderNodeBsdfTransparent")
      transparent_node.location = (400, 200)
      greater_than_node = nodes.new("ShaderNodeMath")
      greater_than_node.operation = "GREATER_THAN"
      greater_than_node.inputs[1].default_value = 0.25
      greater_than_node.location = (400, 0)
      mixrgb_node = nodes.new("ShaderNodeMixRGB")
      mixrgb_node.blend_type = "MULTIPLY"
      mixrgb_node.location = (200, 200)
      pupil_image_node = nodes.new("ShaderNodeTexImage")
      pupil_image_node.image = bpy.data.images["hitomi.png"]
      pupil_image_node.location = (0, -300)
      image_nodes.append(pupil_image_node)
      
      link = links.new(image_node.outputs[0], mixrgb_node.inputs[1])
      link = links.new(pupil_image_node.outputs[0], mixrgb_node.inputs[2])
      link = links.new(pupil_image_node.outputs[1], mixrgb_node.inputs[0])
      link = links.new(mixrgb_node.outputs[0], toon_node.inputs[0])
      link = links.new(image_node.outputs[1], greater_than_node.inputs[0])
      link = links.new(greater_than_node.outputs[0], mix_node.inputs[0])
      link = links.new(transparent_node.outputs[0], mix_node.inputs[1])
      link = links.new(toon_node.outputs[0], mix_node.inputs[2])
      link = links.new(mix_node.outputs[0], output_node.inputs[0])
    else:
      # Everything else. Need transparent backgrounds.
      mix_node = nodes.new("ShaderNodeMixShader")
      mix_node.location = (600, 200)
      transparent_node = nodes.new("ShaderNodeBsdfTransparent")
      transparent_node.location = (400, 200)
      greater_than_node = nodes.new("ShaderNodeMath")
      greater_than_node.operation = "GREATER_THAN"
      greater_than_node.inputs[1].default_value = 0.25 # This is to make the transparency binary
      greater_than_node.location = (400, 0)
      
      link = links.new(image_node.outputs[0], toon_node.inputs[0])
      link = links.new(image_node.outputs[1], greater_than_node.inputs[0])
      link = links.new(greater_than_node.outputs[0], mix_node.inputs[0])
      link = links.new(transparent_node.outputs[0], mix_node.inputs[1])
      link = links.new(toon_node.outputs[0], mix_node.inputs[2])
      link = links.new(mix_node.outputs[0], output_node.inputs[0])

# Change the texture wrapping mode again, but this time for cycles.
for tex_image_name, wrap_mode in tex_wrap_mode_for_image_name.items():
  for image_node in image_nodes:
    if image_node.image.name == tex_image_name:
      image_node.extension = wrap_mode

# Use the compositor to render the eyes and eyebrows on a separate layer from the rest of the model, and then layer that on top to simulate the eye z-indexing through the hair effect.
# Create a new render layer and put only the eyes and eyebrows on it.
eyes_and_eyebrows_layer = scene.render.layers.new("eyes and eyebrows layer")
eyes_and_eyebrows_layer.layers = [i == 1 for i in range(len(eyes_and_eyebrows_layer.layers))]
for obj in scene.objects:
  if obj.data.__class__ == bpy.types.Mesh:
    if obj.data.materials[0].name in ["m1eyeL", "m4eyeR", "m8mayuL", "m11mayuR"]:
      obj.layers = [i == 1 for i in range(len(obj.layers))]
main_layer = scene.render.layers["RenderLayer"]
main_layer.layers = [i == 0 for i in range(len(main_layer.layers))]
main_layer.layers_exclude = [i == 1 for i in range(len(main_layer.layers))] # Stop the eyes from casting shadows on the body
eyes_and_eyebrows_layer.layers_exclude = [i == 0 for i in range(len(main_layer.layers))] # Also stop the body from casting shadows on the hair
scene.layers = [True for i in range(len(scene.layers))]

scene.use_nodes = True
nodes = scene.node_tree.nodes
links = scene.node_tree.links
for node in nodes:
  nodes.remove(node)

layer1_node = nodes.new("CompositorNodeRLayers")
layer1_node.layer = "RenderLayer"
layer1_node.location = (0, 400)

layer2_node = nodes.new("CompositorNodeRLayers")
layer2_node.layer = "eyes and eyebrows layer"
layer2_node.location = (0, 0)

alpha_over_node = nodes.new("CompositorNodeAlphaOver")
alpha_over_node.location = (200, 200)

output_node = nodes.new('CompositorNodeComposite')   
output_node.location = (400, 200)

link = links.new(layer1_node.outputs[0], alpha_over_node.inputs[1])
link = links.new(layer2_node.outputs[0], alpha_over_node.inputs[2])
link = links.new(alpha_over_node.outputs[0], output_node.inputs[0])

# Render the hero clothes preview.
if not os.path.exists(preview_dir):
  os.mkdir(preview_dir)
bpy.data.images["linktexS3TC.png"].filepath = orig_linktexS3TC_path
update_objects_hidden_in_render("hero")
scene.render.filepath = os.path.join(preview_dir, "preview_hero.png")
bpy.ops.render.render(write_still=True)

# Render the casual clothes preview.
bpy.data.images["linktexS3TC.png"].filepath = casual_clothes_tex_path
update_objects_hidden_in_render("casual")
scene.render.filepath = os.path.join(preview_dir, "preview_casual.png")
bpy.ops.render.render(write_still=True)

# Delete temp dir.
shutil.rmtree(temp_dir)
