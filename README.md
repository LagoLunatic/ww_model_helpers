
## About

This is a set of helper scripts to make converting Wind Waker models back and forth between formats easier - specifically for making custom player models to replace Link.

## Getting set up

First download and extract the helper scripts: https://github.com/LagoLunatic/ww_model_helpers/releases/latest

Then you should download SuperBMD, which is the program that actually converts the models: https://github.com/LagoLunatic/SuperBMD/releases/latest  
Extract the contents of the SuperBMD zip and put them in a folder named `SuperBMD` inside the WW Model Helpers folder - in other words, the SuperBMD folder must be next to extract_models.exe and pack_player.exe.  
You should also install the .NET Framework 4.6.1 if you don't already have it installed, as it is required for SuperBMD to run: https://www.microsoft.com/en-us/download/details.aspx?id=49981

It's also recommended that you download J3D Model Viewer: https://github.com/LagoLunatic/J3D-Model-Viewer/releases/latest  
This program allows you to view models in Wind Waker's model formats (BMD and BDL) the way they would actually appear in game. It can even load and preview animations. This makes it much faster to preview changes you make to a model than it would be to load up Wind Waker itself with the changed model.

You will also need a 3D modeling program. I recommend Blender because it's free and is known to work for modifying Wind Waker models: https://www.blender.org/  
Note that you should use Blender 2.79. Blender 2.78 and earlier don't work - they screw up the model's skeleton when importing or exporting the .dae file.

## Tutorial

This basic tutorial will go over the process of converting Link's main model and a couple extras from Wind Waker's format (BDL) to a COLLADA .dae file (which can be modified in regular modeling programs such as Blender) and then back to Wind Waker's format (BDL) and getting the model ingame.  
This tutorial does not go over the process of actually modeling and rigging a custom model.

### Step 1: Set up workspace folders.  
Create two folders - `Link Original` and `Custom Model`. The names of the folders don't matter, but one will be for holding Link's vanilla unmodified model, and the other will be for your custom player model.

### Step 2: Extract Link's original model.  
To get Link's original model, you must first extract all the files from your Wind Waker ISO. You can do this with Dolphin. Right click vanilla Wind Waker in Dolphin's game list, click Properties, Filesystem, right click on Disc, and click Extract Entire Disc.

Once all files have finished extracting, find the file `files/res/Object/Link.arc`. This is an archive file containing all of Link's models and textures, including the items he holds.  
Copy Link.arc to your `Link Original` folder.

Then run the following command:  
`extract_models.exe "path/to/Link Original/Link.arc"`  
That will extract all of the models and textures that are inside the Link.arc archive.  
If everything worked correctly, your `Link Original` folder should now have 57 subfolders (54 which have a model in them and 3 which have animations in them), 3 PNG images, 3 .bti files of the same name as the images (these are the images before being decoded), and it should also still have Link.arc in it.

### Step 3: Copy the files you want to edit.  
The `Link Original` folder needs to have the original models in it, so before modifying anything let's make a copy of them in the `Custom Model` folder.  
For the sake of this tutorial we'll copy the `cl` folder (containing Link's main model), the `hands` folder (containing the model for Link's various hand poses), the `katsura` folder (containing the model for the back of Link's hair when he's in his casual clothes), and `linktexbci4.png` (Link's texture for when he's in his casual clothes).

But if you want to modify other files, you would copy those as well (e.g. copy the `pring` folder if you want to modify the Power Bracelets). You shouldn't copy folders for any models you don't intend to modify.  
You can find a full list of what all models and textures inside Link.arc are in the link_models_and_textures.txt file included with these scripts.

### Step 4: Open the model.  
Now you can open Link's model in a 3D modeling program. This tutorial will assume you use Blender, but other modeling programs probably work too.  
Open Blender, delete all default objects in the scene, and go to File -> Import -> Collada (.dae). Then choose the file `Custom Model/cl/cl.dae`. Now you have Link's model open.  
You could modify it now if you want, but for the sake of this tutorial just leave it alone for now.

Note that the process of importing and exporting .dae files is lossy, so if you do it too many times the model will get completely screwed up. Therefore, you should only import each model's .dae one time, and then save it as a .blend (or whatever the equivalent is if you're not using Blender).  
So after importing `cl.dae`, you should go to Save As and save `cl.blend` right next to `cl.dae`. From now on you can open and resave `cl.blend` as many times as you want and the model will never get messed up.

### Step 4.5: Fix the imported model in Blender.

Now that you have the model in Blender, you might notice that the shading on parts of the model looks wrong. For example, around Link's mouth. This is because Blender's .dae importer currently does not import custom normals from the .dae file.  
In order to fix the normals, use Blender's text editor to open the script named `fix_normals.py` that comes with the WW Model Helpers download. Click "Run Script", and it should automatically fix the shading on Link's mouth and such.

Another issue is that Blender is displaying the model without any textures. It's not strictly necessary, but if you want to see textures, first change Blender's view mode to Material. Then open the script named `make_materials_shadeless.py` that comes with the WW Model Helpers download, and click "Run Script".  
If the model displays as completely white after doing this, your model might not have any textures imported with it. This can be caused by you moving the texture .png files after extracting them from the model but before importing the model into Blender - the .dae file stores the paths to the textures as absolute paths on your hard drive, so moving them will cause Blender to not be able to find them.

### Step 5: Create your custom model.  

Once you have Link's vanilla model imported correctly, you can get to work starting to edit it to make your custom model.  
This tutorial will not cover the process of making a model, only the process of using the scripts to convert between formats.  
However, you can refer to [this other tutorial](https://docs.google.com/document/d/1AuI9OHi6Ni2HUzyBf_djT5wa1gzVmN2SG3jbROtrFKw) for extra information about swapping meshes and materials and rigging your custom model.

### Step 6: Convert the model back to Wind Waker's format.  
Open `cl.blend` and go to File -> Export -> Collada (.dae). Then choose to overwrite the file `Custom Model/cl/cl.dae`.

Then run this command:  
`pack_player.exe -link "path/to/Link Original" -custom "path/to/Custom Model"`

What pack_player does is automate converting the .dae models in all the folders of your `Custom Model` folder to .bdl models which can be used by the game itself.  
It also converts any .png images back to .bti images that the game can use.  
Then, it packs all of Link's models and textures into a new Link.arc, which is located in your `Custom Model` folder.

Note: pack_player supports all of the models and textures in Link.arc, but a few of the models cannot be properly repacked by SuperBMD currently. Refer to link_models_and_textures.txt for a list of what all the models and textures are and any technical limitations on specific models.  

Note: By default, pack_player will modify the texture of hands.bdl, but not the model itself. If you want to edit the shape of the hand poses in hands.bdl, you need to pass the -repackhands argument like so:  
`pack_player.exe -link "path/to/Link Original" -custom "path/to/Custom Model" -repackhands`

### Step 7: Preview the changed model in J3D Model Viewer (optional).

Before putting your new model in game, it's a good idea to load it up in J3D Model Viewer and make sure it looks right there. If it doesn't, you don't need to waste your time replacing the game's model and booting the game up.

Simply open J3D Model Viewer, and then open your `Custom Model/cl/cl.bdl` model that was created by pack_player.  
In the viewer, hold down the right mouse button and press the WASDQE keys to move the camera around. Scroll the mouse wheel to change movement speed.

Next, you might want to try loading an animation. But first you need to find where Link's animations are stored.  
You might notice three folders in your `Link Original` folder named `#Bone animations`, `#TEV register animations`, and `#Texture animations`. These contain the animations that were in Link.arc, but those aren't animations for Link's main body, but for miscellaneous models in Link.arc.  
Link's main body's animations are stored in the archive `files/res/Object/LkAnm.arc`. To get the animations out of it, repeat the same process you used to extract Link.arc.  
First copy LkAnm.arc to a new folder somewhere else named `Link Animations` or whatever you want.  
Then run `extract_models.exe "path/to/Link Animations/LkAnm.arc"`.  
Then back in J3D Model Viewer, you can load an animation by going to File -> Load Animation, and selecting one of the .bck files in `Link Animations/#Bone animations`.

### Step 8: Load the custom model in game.

The Link.arc created by pack_player is ready to be used by Wind Waker.  
To have the randomizer load it, simply create a new folder inside the randomizer's `models` folder, and name the new folder what you want your custom model to be named. Then put your new Link.arc inside this new folder. When you boot up the randomizer, you can select your custom model from the dropdown list.

Alternatively, if you want to use the model in the vanilla game, replace the file files/res/Object/Link.arc with the new Link.arc.

If everything went well, the game should load up correctly with no crashes or visual errors.

## Running the scripts from source

Download and install git from here: https://git-scm.com/downloads  
Then clone this repository with git by running this in a command prompt:  
`git clone --recurse-submodules https://github.com/LagoLunatic/ww_model_helpers.git`  

Download and install Python 3.6.6 from here: https://www.python.org/downloads/release/python-366/  
"Windows x86-64 executable installer" is the one you want if you're on Windows.  

Then run `cd ww_model_helpers`, followed by `py -3.6 -m pip install -r wwrando/requirements.txt` to install dependencies.  

Finally, you can run the scripts with these commands:  
`py -3.6 extract_models.py`  
`py -3.6 pack_player.py`  
