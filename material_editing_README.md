
## Table of contents

* [Material editing](#material-editing)
* [Beginner](#beginner)
 * [Face culling](#face-culling)
* [Intermediate](#intermediate)
* [Advanced](#advanced)

## Material editing

Materials control how a 3D model is rendered in game. They control things like transparency, shininess, and more.  
The materials for a BDL/BMD model can be found in the materials.json file that is created when you unpack the model. You can edit this file in any text editor, but it can more complex than other aspects of model editing because of how many options there are.

This won't be a fully comprehensive guide on how to do everything that is possible with materials.json, but rather a list of some specific things that are frequently useful when making custom models for Wind Waker.  

When you want to edit a specific material, you first need to find it in materials.json. For example, if you want to edit the material for Link's hat, select his hat mesh in your 3D modeling program of choice and look at the name of the material - it should be `ear(3)`.  
If you open materials.json and Ctrl+F for `"ear(3)"` (preferably with quotes), it will bring you to the first line of the hat's material entry. You can then edit this entry following instructions in the other parts of this guide, and then repack the model to change how the hat looks.  

### Beginner

#### Face culling

One of the easiest to edit and most useful properties is `CullMode`, which affects which side(s) of the mesh's faces will be hidden. It has the following options:
* `None` - Both the front and back of the mesh will be visible.
* `Front` - Only the back of the mesh will be visible.
* `None` - Only the front of the mesh will be visible.

One use for this is when you want to have a thin mesh (such as a cape) and don't want to waste polygons creating both a front and a back for the mesh. You can have just one layer of polygons and set the face culling to `None` so that the mesh if visible from both sides.

### Intermediate

### Advanced
