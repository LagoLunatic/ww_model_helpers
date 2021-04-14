
## Table of contents

* [Material editing](#material-editing)
* [Beginner](#beginner)
  * [Face culling](#face-culling)
  * [Binary transparency (alpha masking)](#binary-transparency-alpha-masking)
* [Intermediate](#intermediate)
  * [Partial transparency (alpha blending)](#partial-transparency-alpha-blending)
  * [Changing color tint](#changing-color-tint)
  * [Removing texture scrolling/scaling](#removing-texture-scrolling-scaling)
* [Advanced](#advanced)
  * [Shiny materials](#shiny-materials)
  * [Transparenct hiny materials](#transparent-shiny-materials)
  * [Outlines](#outlines)
* [Other properties](#other-properties)

## Material editing

Materials control how a 3D model is rendered in game. They control things like transparency, shininess, and more.  
The materials for a BDL/BMD model can be found in the materials.json file that is created when you unpack the model. You can edit this file in any text editor, but it can more complex than other aspects of model editing because of how many options there are.

This won't be a fully comprehensive guide on how to do everything that is possible with materials.json, but rather a list of some specific things that are frequently useful when making custom models for Wind Waker.  

When you want to edit a specific material, you first need to find it in materials.json. For example, if you want to edit the material for Link's hat, select his hat mesh in your 3D modeling program of choice and look at the name of the material - it should be `ear(3)`.  
If you open materials.json and Ctrl+F for `"ear(3)"` (preferably with quotes), it will bring you to the first line of the hat's material entry. You can then edit this entry following instructions in the other parts of this guide, and then repack the model to change how the hat looks.  
If you want to change how multiple meshes render, you have to edit each of their materials individually.  

## Beginner

### Face culling

One of the easiest to edit and most useful properties is `CullMode`, which affects which side(s) of the mesh's faces will be hidden. It has the following options:
* `None` - Both the front and back of the mesh will be visible.
* `Front` - Only the back of the mesh will be visible.
* `None` - Only the front of the mesh will be visible.

One use for this is when you want to have a thin mesh (such as a cape) and don't want to waste polygons creating both a front and a back for the mesh. You can have just one layer of polygons and set the face culling to `None` so that the mesh if visible from both sides.

### Binary transparency (alpha masking)

Binary transparency (also known as alpha masking) allows meshes to render transparent textures. However, it only allows pixels to be either fully transparent or fully opaque - if you want to have a smooth gradient of transparency, see the [Partial transparency (alpha blending)](#partial-transparency-alpha-blending) section instead.  

Before making the material support transparency, first make sure that the texture itself is set up to support alpha transparency. In tex_headers.json, find the texture for your mesh and look at the `Format` field. The following texture formats support transparency:
* `IA4` (greyscale, 4 bits of alpha)
* `IA8` (greyscale, 8 bits of alpha)
* `RGB5A3` (color, 3 bits of alpha)
* `RGBA32` (color, 8 bits of alpha, large filesize)
* `C4` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C8` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C14X2` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `CMPR` (color, 1 bit of alpha)

If the texture doesn't use a format that supports transparency, change it to one that does.  
CMPR may be a good choice because more than 1 bit of alpha isn't necessary for binary transparency anyway.

Next, you can edit the material itself to have binary transparency. To do this, simply find the part of the material called `"AlphCompare"`, and replace that section with the following:
```
    "AlphCompare": {
      "Comp0": "GEqual",
      "Reference0": 128,
      "Operation": "And",
      "Comp1": "LEqual",
      "Reference1": 255
    },
```
That will cause pixels with an alpha value of less than 128 to be fully transparent and not render at all. You can tweak the 128 number if you want the cutoff point to be elsewhere.

## Intermediate

### Partial transparency (alpha blending)

Partial transparency (also known as alpha blending) allows meshes to render transparent textures. Unlike [Binary transparency (alpha masking)](#binary-transparency-alpha-masking), partial transparency supports smooth gradients of transparency, although it's a bit more finicky than binary transparency and may sometimes cause things to render strangely if not set up correctly.

Before making the material support transparency, first make sure that the texture itself is set up to support alpha transparency. In tex_headers.json, find the texture for your mesh and look at the `Format` field. The following texture formats support transparency:
* `IA4` (greyscale, 4 bits of alpha)
* `IA8` (greyscale, 8 bits of alpha)
* `RGB5A3` (color, 3 bits of alpha)
* `RGBA32` (color, 8 bits of alpha, large filesize)
* `C4` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C8` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C14X2` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `CMPR` (color, 1 bit of alpha)

If the texture doesn't use a format that supports transparency, change it to one that does.  
C8 with the `PaletteFormat` set to `RGB5A3` is generally a good choice as it supports both color and 3 bits of alpha, without making the filesize too large.  
Do not use CMPR for partial transparency, as it only supports 1 bit of alpha making it effectively the same as binary transparency.

Next, you can edit the material itself to have partial transparency. To do this, find the part of the material called `"BMode"`, which should also have a section called `"ZMode"` right after it. Replace both of those sections with the following:
```
    "BMode": {
      "Type": "Blend",
      "SourceFact": "SrcAlpha",
      "DestinationFact": "InverseSrcAlpha",
      "Operation": "Copy"
    },
    "ZMode": {
      "Enable": true,
      "Function": "LEqual",
      "UpdateEnable": false
    },
```

Additionally, you will probably also want to disable binary transparency so that it doesn't interfere with partial transparency. Find the `"AlphCompare"` section right above the `"BMode"` section, and replace it with the following:
```
    "AlphCompare": {
      "Comp0": "Always",
      "Reference0": 0,
      "Operation": "Or",
      "Comp1": "Always",
      "Reference1": 0
    },
```
You don't necessarily have to disable binary transparency if you don't want to - it does work along with partial transparency, it just may give undesired results.

### Changing color tint

TODO

### Removing texture scrolling/scaling

Sometimes, you might edit a model that animates its textures and makes them scroll or scale. If you don't want these animations to apply to your custom model, the easiest way to disable them is to replace the material's texture matrix source with the identity matrix.  

To do this, find the `"Tex1CoordGens"` section of the material, which may look like this:
```
    "TexCoord1Gens": [
      {
        "Type": "Matrix2x4",
        "Source": "Tex0",
        "TexMatrixSource": "TexMtx0"
      },
      {
        "Type": "SRTG",
        "Source": "Color0",
        "TexMatrixSource": "Identity"
```
Change all of the instances of `TexMtx0`, `TexMtx1`, etc, into `Identity`.

## Advanced

### Shiny materials

TODO

### Transparent shiny materials

TODO

### Outlines

TODO

## Other properties

If you want to edit materials in a way not covered in the guide above, you'll have to figure out how by yourself.  
The easiest way to do this is generally to find a material from the vanilla game that already does what you want, and try copying that material (or part of it) over your custom material.  

If what you want to do isn't done in any of the vanilla materials, you'll need to try various things via trial and error to see if you can get the desired effect. There's currently no comprehensive explanation of what all of the dozens of material properties do, so there's no easy way to figure that out.  
However, SuperBMD's source code does have [lists of what possible values of each property can be](https://github.com/LagoLunatic/SuperBMD/tree/master/SuperBMDLib/source/Materials/Enums). For example, `TevOp.cs` lists out the possible values for the `ColorOp` and `AlphaOp` properties of the `TevStages` section - `Add`, `Sub`, etc.  
