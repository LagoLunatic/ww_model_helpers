
## About

This is a set of helper scripts to make converting Wind Waker models back and forth between formats easier - specifically for making custom player models to replace Link.

## Getting set up

First download and extract the helper scripts: https://github.com/LagoLunatic/ww_model_helpers/releases/latest

Then you should download SuperBMD, which is the program that actually converts the models: https://github.com/LagoLunatic/SuperBMD/releases/latest  
Extract the contents of the SuperBMD zip and put them in the empty SuperBMD folder inside the ww_model_helpers folder.

It's also recommended that you download J3D Model Viewer: https://github.com/LordNed/J3D-Model-Viewer/releases/latest  
This program allows you to view models in Wind Waker's model formats (BMD and BDL) the way they would actually appear in game. It can even load and preview animations. This makes it much faster to preview changes you make to a model than it would be to load up Wind Waker itself with the changed model.

## Tutorial

This basic tutorial will go over the process of converting Link's main model and a couple extras from Wind Waker's format (BDL) to a COLLADA .dae file (which can be modified in regular modeling programs such as Blender) and then back to Wind Waker's format (BDL) and getting the model ingame.  
Currently this tutorial does not go over the process of actually modeling and rigging a custom model.

### Step 1: Set up workspace folders.  
Create two folders - `Link Original` and `Custom Model`. The names of the folders don't matter, but one will be for holding Link's vanilla unmodified model, and the other will be for your custom player model.

### Step 2: Extract Link's original model.  
To get Link's original model, you must first extract all the files from your Wind Waker ISO. You can do this with Dolphin. Right click vanilla Wind Waker in Dolphin's game list, click Properties, Filesystem, right click on Disc, and click Extract Entire Disc.

Once all files have finished extracting, find the file `files/res/Object/Link.arc`. This is an archive file containing all of Link's models and textures, including the items he holds.  
Copy Link.arc to your `Link Original` folder.

Then run the following command:  
`extract_models.exe "path/to/Link Original/Link.arc"`  
That will extract all of the models and textures that are inside the Link.arc archive.  
If everything worked correctly, your `Link Original` folder should now have 54 subfolders, each containing a different model, 3 PNG images, 3 .bti files of the same name as the images (these are the images before being decoded), and it should also still have Link.arc in it.

### Step 3: Copy the files you want to edit.  
The `Link Original` folder needs to have the original models in it, so before modifying anything let's make a copy of them in the `Custom Model` folder.  
For the sake of this tutorial we'll copy the `cl` folder (containing Link's main model), the `katsura` folder (containing the model for the back of Link's hair when he's in his casual clothes), and `linktexbci4.png` (Link's texture for when he's in his casual clothes). But if you want to modify other files, you would copy those as well (e.g. copy the `pring` folder if you want to modify the Power Bracelets). The only thing you absolutely have to copy is `cl`.

### Step 4: Open the model.  
Now you can open Link's model in a 3D modeling program. This tutorial will assume you use Blender, but other modeling programs probably work too.  
Open Blender, delete all default objects in the scene, and go to File -> Import -> Collada (.dae). Then choose the file `Custom Model/cl/cl.dae`. Now you have Link's model open.  
You could modify it now if you want, but for the sake of this tutorial just leave it alone for now.

Note that the process of importing and exporting .dae files is lossy, so if you do it too many times the model will get completely screwed up. Therefore, you should only import each model's .dae one time, and then save it as a .blend (or whatever the equivalent is if you're not using Blender).  
So after importing `cl.dae`, you should go to Save As and save `cl.blend` right next to `cl.dae`. From now on you can open and resave `cl.blend` as many times as you want and the model will never get messed up.

You might notice that Blender is displaying the model without any textures. If you want to see textures, first change Blender's view mode to Material. Then go through all of Link's materials one by one and check the Shadeless checkbox. But that gets pretty tedious, so you can automate checking Shadeless for all materials by running this simple Python script within Blender's text editor:  
```
import bpy
for item in bpy.data.materials:
  item.use_shadeless = True
```
If the model displays as completely white after doing this, your model might not have any textures imported with it. This can be caused by you moving the texture .png files after extracting them from the model but before importing the model into Blender - the .dae file stores the paths to the textures as absolute paths on your hard drive, so moving them will cause Blender to not be able to find them.

### Step 5: Convert the model back to Wind Waker's format.  
Open `cl.blend` and go to File -> Export -> Collada (.dae). Then choose to overwrite the file `Custom Model/cl/cl.dae`.

Then run this command:  
`pack_player.exe -link "path/to/Link Original" -custom "path/to/Custom Model"`

What pack_player does is automate converting the .dae models in all the folders of your `Custom Model` folder to .bdl models which can be used by the game itself.  
It also converts any .png images back to .bti images that the game can use.  
Then, it packs all of Link's models and textures into a new Link.arc, which is located in your `Custom Model` folder.

Note: Currently pack_player does not support all of Link's models and textures. The only ones it supports at the moment are:
* cl.bdl (Link's main model)
* katsura.bdl (casual clothes hair)
* linktexbci4.bti (casual clothes texture)
* pring.bdl (Power Braclets)

### Step 6: Preview the changed model in J3D Model Viewer (optional).

Before putting your new model in game, it's a good idea to load it up in J3D Model Viewer and make sure it looks right there. If it doesn't, you don't need to waste your time replacing the game's model and booting the game up.

Simply open J3D Model Viewer, and then open your `Custom Model/cl/cl.bdl` model that was created by pack_player.  
In the viewer, hold down the right mouse button and press the WASDQE keys to move the camera around. Scroll the mouse wheel to change movement speed.

Next, you might want to try loading an animation. But first you need to find where Link's animations are stored.  
You might notice three folders in your `Link Original` folder named `#Bone animations`, `#TEV register animations`, and `#Texture animations`. These contain the animations that were in Link.arc, but those aren't animations for Link's main body, but for miscellaneous models in Link.arc.  
Link's main body's animations are stored in the archive `files/res/Object/LkAnm.arc`. To get the animations out of it, repeat the same process you used to extract Link.arc.  
First copy LkAnm.arc to a new folder somewhere else named `Link Animations` or whatever you want.  
Then run `extract_models.exe "path/to/Link Animations/LkAnm.arc"`.  
Then back in J3D Model Viewer, you can load an animation by going to File -> Load Animation, and selecting one of the .bck files in `Link Animations/#Bone animations`.

### Step 7: Load the custom model in game.

The Link.arc created by pack_player is ready to be used by Wind Waker.  
To have the randomizer load it, simply create a new folder inside the randomizer's `models` folder, and name the new folder what you want your custom model to be named. Then put your new Link.arc inside this new folder. When you boot up the randomizer, you can select your custom model from the dropdown list.

Alternatively, if you want to use the model in the vanilla game, replace the file files/res/Object/Link.arc with the new Link.arc.

If everything went well, the game should load up correctly with no crashes or visual errors.
