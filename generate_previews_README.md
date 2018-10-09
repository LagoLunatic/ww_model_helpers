
The script to render the preview images and masks, generate_previews.py, should be run from within the .blend file for the custom player character's main model.
The script requires several files to be in specific places in order for it to work right.
If something goes wrong when running the script, Blender will say "Python script fail, look in the console". You can open the console to see the specific error by going to Window -> Toggle System Console. Also, any time the script fails you should remember to Ctrl-Z in order to undo anything the script might have messed up.

The required folder structure for running the script is as follows:
- Custom Model (the main folder for your model, the name of the folder doesn't matter)
  - linktexbci4.png (the casual clothes texture)
  - cl (main model folder)
    - cl.bdl
    - cl.blend (the main blend file you will run the script from - the name doesn't matter, but the folder it's in does)
    - hitomi.png
    - tex_headers.json
    - metadata.txt
    - color_masks (a folder containing all of the red and white masks for your model's custom colors)
  - katsura (casual hair model folder)
    - katsura.blend

If the script runs successfully with no errors, a preview folder should have been created inside the cl folder. This preview folder should have a render of your model in hero's clothes, a render your model in casual clothes, and one color mask for each custom color.
If they look correct, you can just move the entire preview folder into the folder the randomizer will load the custom model from (so that it's next to Link.arc). Then test it out in the randomizer to make sure it works correctly.
