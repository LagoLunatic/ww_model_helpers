
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

context = bpy.context
scene = context.scene
world = bpy.data.worlds[0]
view_layer = context.view_layer

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

view_layer.objects.active = scene.objects[0]
bpy.ops.object.mode_set(mode="OBJECT")

# Append the casual hair mesh.
casual_hair_model_mesh_name = "mesh-0"
bpy.ops.wm.append(
  directory=casual_hair_model_path + "\\Object\\", # Needs to have a trailing slash
  filename=casual_hair_model_mesh_name,
)

# Pose the model so it's not T-posing.
skeleton_root = scene.objects["skeleton_root"]
view_layer.objects.active = skeleton_root
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
    orig_tex_names_for_objs[obj] = obj.data.materials[0].node_tree.nodes["Image Texture"].image.name

def update_objects_hidden_in_render(prefix):
  for obj in scene.objects:
    if obj.data.__class__ == bpy.types.Mesh:
      if obj.data.materials[0].name == hat_material_name:
        # Hide the hat mesh in casual clothes.
        should_hide = (prefix == "casual")
      elif obj.data.materials[0].name == belt_buckle_material_name:
        # Hide the belt buckle mesh in casual clothes.
        should_hide = (prefix == "casual")
      elif orig_tex_names_for_objs[obj] == "katsuraS3TC.png":
        # Hide the casual hair mesh in hero clothes.
        should_hide = (prefix == "hero")
      elif orig_tex_names_for_objs[obj] == "podAS3TC.png":
        # Hide the sword sheath mesh.
        should_hide = True
      elif obj.data.materials[0].name in ["m2eyeLdamA", "m3eyeLdamB", "m5eyeRdamA", "m6eyeRdamB"]:
        # Hide the duplicate eye meshes.
        should_hide = True
      elif obj.data.materials[0].name in ["m9mayuLdamA", "m10mayuLdamB", "m12mayuRdamA", "m13mayuRdamB"]:
        # Hide the duplicate eyebrow meshes.
        should_hide = True
      else:
        # Show every other mesh.
        should_hide = False
      
      obj.hide_render = should_hide
      
      # Hide the object from all view layers that it is in.
      for this_view_layer in scene.view_layers:
        this_view_layer_objects = [obj for obj in this_view_layer.objects]
        if obj in this_view_layer_objects:
          obj.hide_set(should_hide, view_layer=this_view_layer)

update_objects_hidden_in_render("hero")

# Set the render resolution.
# The randomizer will display it at 225x350 to the user.
# But we render it at twice that size so the randomizer can work with the non-antialiased render, and then scale it down to get antialiasing.
scene.render.resolution_x = 225*2
scene.render.resolution_y = 350*2
scene.render.resolution_percentage = 100

# Make the background transparent.
scene.render.film_transparent = True

# Masks need to be binary, they won't work properly if they have antialiasing.
scene.render.filter_size = 0.01

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
camera.data.lens = 35.0
camera.data.sensor_width = 32.0

# Add lighting.
lamps = []
for lamp_i in range(2):
  bpy.ops.object.light_add(
    type="SUN",
    location=(17, -82, 100),
    rotation=(math.radians(75), math.radians(15), math.radians(0)),
  )
  lamp = context.object
  lamps.append(lamp)
  lamp.data.angle = math.radians(4) # Make the toon shading shadow edges a little bit softer.
  lamp.data.energy = 0.45


# Scale the whole scene down to 1/20th normal size because there would be rendering artifacts (possibly z-fighting) in the masks at normal scale, such as black dots where the eyes overlap the face and white/red lines where the pants touch the skirt.
# Note that we can't select all and then scale - this works fine in Blender's UI but results in Link's pose becoming all weird and distorted if done via Python.
bpy.ops.object.select_all(action="DESELECT")
skeleton_root.select_set(True)
casual_hair_skeleton_root = casual_hair_mesh.parent
casual_hair_skeleton_root.select_set(True)
camera.select_set(True)
for lamp in lamps:
  lamp.select_set(True)
bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))


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

model_metadata = {}
with open(model_metadata_path) as f:
  for line in f.readlines():
    match = re.search(r"^([^\s:]+): (.+)$", line)
    if match:
      key = match.group(1)
      val = match.group(2).strip()
      if val.lower() == "true":
        val = True
      elif val.lower() == "false":
        val = False
      model_metadata[key] = val

# Now generate the masks by replacing the model's textures with the texture masks.

# Make a copy of all images so we can change those into the masks.
orig_images = list(bpy.data.images)
for image in orig_images:
  if len(image.pixels) == 0:
    continue
  
  temp_img_path = os.path.join(temp_dir, image.name)
  image.save_render(filepath=temp_img_path)
  mask_image = bpy.data.images.load(temp_img_path)
  mask_image.name = image.name + "_mask"

orig_linktexS3TC_path = bpy.data.images["linktexS3TC.png"].filepath

# Modify all the materials to use their respective mask images instead of their texture images.
# Also make the materials all be shadeless since we don't want shading on a mask image.
# To do this we make the material be an emission of the appropriate color - but only when the light path that hits it is a camera ray, so that the emission doesn't light up other things.
for material in bpy.data.materials:
  material.blend_method = "CLIP" # Enable alpha clipping
  
  nodes = material.node_tree.nodes
  links = material.node_tree.links
  
  if "Image Texture" in nodes:
    tex_image_node = nodes["Image Texture"]
    material_output_node = nodes["Material Output"]
    mask_image = bpy.data.images[tex_image_node.image.name + "_mask"]
    
    mask_image_node = nodes.new("ShaderNodeTexImage")
    mask_image_node.image = mask_image
    # Don't blur the borders between red and white on the masks with image interpolation.
    mask_image_node.interpolation = "Closest"
    mask_image_node.location = (-300, 600)
    
    # Set the texture wrapping type for the material from the tex_headers.json.
    if tex_image_node.image.name in tex_wrap_mode_for_image_name:
      mask_image_node.extension = tex_wrap_mode_for_image_name[tex_image_node.image.name]
    
    emission_node = nodes.new("ShaderNodeEmission")
    # Set the emission strength high so it's exactly the desired color and not washed out.
    emission_node.inputs[1].default_value = 10
    emission_node.location = (0, 600)
    
    transparent_node = nodes.new("ShaderNodeBsdfTransparent")
    transparent_node.location = (0, 700)
    
    mix_shader_node = nodes.new("ShaderNodeMixShader")
    mix_shader_node.location = (200, 600)
    
    links.new(mask_image_node.outputs[0], emission_node.inputs[0])
    links.new(mask_image_node.outputs[1], mix_shader_node.inputs[0])
    links.new(transparent_node.outputs[0], mix_shader_node.inputs[1])
    links.new(emission_node.outputs[0], mix_shader_node.inputs[2])
    links.new(mix_shader_node.outputs[0], material_output_node.inputs[0])


# Use the compositor to render the eyes and eyebrows on a separate layer from the rest of the model, and then layer that on top to simulate the eye z-indexing through the hair effect.
# Create a new render layer and put only the eyes and eyebrows on it.
orig_view_layer = context.window.view_layer
orig_collection = scene.collection.children[0]
# Create the view layer and collection for the eyes and eyebrows.
bpy.ops.scene.view_layer_add()
eyes_and_eyebrows_layer = scene.view_layers[-1]
eyes_and_eyebrows_layer.name = "eyes and eyebrows layer"
eyes_and_eyebrows_collection = bpy.data.collections.new("eyes and eyebrows collection")
scene.collection.children.link(eyes_and_eyebrows_collection)
# Move the eyes, eyebrows, and hair into their appropriate collections.
for obj in scene.objects:
  if obj.data.__class__ == bpy.types.Mesh:
    if obj.data.materials[0].name in ["m1eyeL", "m4eyeR", "m8mayuL", "m11mayuR"]:
      eyes_and_eyebrows_collection.objects.link(obj)
      orig_collection.objects.unlink(obj)
  elif isinstance(obj.data, bpy.types.Light):
    # We want lighting to be visible in all collections.
    eyes_and_eyebrows_collection.objects.link(obj)
# Finally hide all but the respective collections from each view layer.
# (But we don't hide the hair from the main body view layer because we want it to cast a shadow on the face.)
orig_view_layer.layer_collection.children["eyes and eyebrows collection"].exclude = True
eyes_and_eyebrows_layer.layer_collection.children[0].exclude = True

scene.use_nodes = True
nodes = scene.node_tree.nodes
links = scene.node_tree.links
for node in nodes:
  nodes.remove(node)

layer1_node = nodes.new("CompositorNodeRLayers")
layer1_node.layer = orig_view_layer.name
layer1_node.location = (0, 800)

layer2_node = nodes.new("CompositorNodeRLayers")
layer2_node.layer = "eyes and eyebrows layer"
layer2_node.location = (0, 0)

alpha_over_node = nodes.new("CompositorNodeAlphaOver")
alpha_over_node.location = (200, 200)

output_node = nodes.new("CompositorNodeComposite")
output_node.location = (800, 200)

links.new(layer1_node.outputs[0], alpha_over_node.inputs[1])
links.new(layer2_node.outputs[0], alpha_over_node.inputs[2])
links.new(alpha_over_node.outputs[0], output_node.inputs[0])


for prefix in ["hero", "casual"]:
  color_mask_file_paths = glob.glob(os.path.join(color_masks_dir, "%s_*.png" % prefix))
  
  update_objects_hidden_in_render(prefix)
  
  has_colored_eyebrows = model_metadata.get("has_colored_eyebrows", False)
  hands_color_name = model_metadata.get(prefix + "_hands_color_name", "Skin")
  mouth_color_name = model_metadata.get(prefix + "_mouth_color_name", "Skin")
  eyebrow_color_name = model_metadata.get(prefix + "_eyebrow_color_name", "Hair")
  casual_hair_color_name = model_metadata.get("casual_hair_color_name", "Hair")
  
  for color_mask_file_path in color_mask_file_paths:
    file_basename = os.path.splitext(os.path.basename(color_mask_file_path))[0]
    assert file_basename.startswith(prefix + "_")
    curr_color_name = file_basename[len(prefix + "_"):]
    
    textures_to_mask = []
    textures_to_not_mask = []
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
    textures_to_not_mask.append("eyeh.1.png")
    
    # Change the textures to be completely red or white, but also preserve the original alpha channel from the texture (not the mask).
    for texture_name in textures_to_mask + textures_to_not_mask:
      mask_image = bpy.data.images[texture_name + "_mask"]
      tex_image = bpy.data.images[texture_name]
      tex_pixels = tex_image.pixels[:] # Convert the image's pixels to a tuple to increase performance when reading from it
      new_pixels = [] # Instead of modifying the image's pixels every loop, make a new list of pixels we edit for better performance
      for i in range(len(mask_image.pixels)//4):
        orig_alpha = tex_pixels[i*4+3]
        if texture_name in textures_to_mask:
          new_pixels += [1.0, 0.0, 0.0, orig_alpha]
        else:
          new_pixels += [1.0, 1.0, 1.0, orig_alpha]
      mask_image.pixels[:] = new_pixels # Now update the image's actual pixels just once with our pixel list
    
    if prefix == "casual":
      bpy.data.images["linktexS3TC.png"].filepath = casual_clothes_tex_path
    else:
      bpy.data.images["linktexS3TC.png"].filepath = orig_linktexS3TC_path
    
    bpy.data.images["linktexS3TC.png_mask"].filepath = os.path.join(color_masks_dir, "%s_%s.png" % (prefix, curr_color_name))
    mask_image = bpy.data.images["linktexS3TC.png_mask"]
    mask_pixels = mask_image.pixels[:]
    tex_image = bpy.data.images["linktexS3TC.png"]
    tex_pixels = tex_image.pixels[:]
    new_pixels = []
    for i in range(len(mask_image.pixels)//4):
      orig_alpha = tex_pixels[i*4+3]
      r = mask_pixels[i*4]
      g = mask_pixels[i*4+1]
      b = mask_pixels[i*4+2]
      new_pixels += [r, g, b, orig_alpha]
    mask_image.pixels[:] = new_pixels # Now update the image's actual pixels just once with our pixel list
    
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




# Now render the actual preview images, with proper toon shading.
scene.render.engine = "CYCLES"
world.light_settings.use_ambient_occlusion = True
world.light_settings.ao_factor = 0.3
scene.cycles.filter_width = 0.01 # Effectively disables antialiasing where meshes meet
scene.view_settings.view_transform = "Standard" # Necessary to fix the colors looking very washed out

# Create the pupil image.
bpy.data.images.load(pupil_image_path)

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
    
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf_node = None
    output_node = None
    for node in mat.node_tree.nodes:
      if node.__class__ == bpy.types.ShaderNodeBsdfDiffuse:
        bsdf_node = node
        break
      elif node.__class__ == bpy.types.ShaderNodeOutputMaterial:
        output_node = node
        break
    if bsdf_node:
      nodes.remove(bsdf_node)
    output_node.location = (800, 400)
    
    image_node = nodes.new("ShaderNodeTexImage")
    image_node.image = bpy.data.images[tex_name]
    image_node.location = (-300, -300)
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
      mixrgb_node.location = (250, 200)
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
