
## Table of contents

* [Material editing](#material-editing)
* [Beginner](#beginner)
  * [Face culling](#face-culling)
  * [Binary transparency (alpha masking)](#binary-transparency-alpha-masking)
  * [Shadeless materials](#shadeless-materials)
* [Intermediate](#intermediate)
  * [Partial transparency (alpha blending)](#partial-transparency-alpha-blending)
  * [Modifying TEV Colors and Konst Colors](#modifying-tev-colors-and-konst-colors)
  * [Changing material color](#changing-material-color)
  * [Removing texture scrolling/scaling](#removing-texture-scrollingscaling)
* [Advanced](#advanced)
  * [Custom TEV Stages](#custom-tev-stages)
  * [Shiny materials](#shiny-materials)
  * [Transparent shiny materials](#transparent-shiny-materials)
  * [Outlines](#outlines)
  * [Vertex colors](#vertex-colors)
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
* `Back` - Only the front of the mesh will be visible.

One use for this is when you want to have a thin mesh (such as a cape) and don't want to waste polygons creating both a front and a back for the mesh. You can have just one layer of polygons and set the face culling to `None` so that the mesh if visible from both sides.

### Binary transparency (alpha masking)

Binary transparency (also known as alpha masking) allows meshes to render transparent textures. However, it only allows pixels to be either fully transparent or fully opaque - if you want to have a smooth gradient of transparency, see the [Partial transparency (alpha blending)](#partial-transparency-alpha-blending) section instead.  

Before making the material support transparency, first make sure that the texture itself is set up to support alpha transparency. In tex_headers.json, find the texture for your mesh and look at the `Format` field. The following texture formats support transparency:
* `IA4` (greyscale, 4 bits of alpha)
* `IA8` (greyscale, 8 bits of alpha)
* `RGB5A3` (color, 3 bits of alpha)
* `RGBA32` (color, 8 bits of alpha, large file size)
* `C4` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C8` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C14X2` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `CMPR` (color, 1 bit of alpha)

If the texture doesn't use a format that supports transparency, change it to one that does.  
CMPR may be a good choice because more than 1 bit of alpha isn't necessary for binary transparency anyway.

Next, you can edit the material itself to have binary transparency. To do this, simply find the part of the material called `"AlphCompare"`, and replace that section with the following:
```json
    "AlphCompare": {
      "Comp0": "GEqual",
      "Reference0": 128,
      "Operation": "And",
      "Comp1": "LEqual",
      "Reference1": 255
    },
```
That will cause pixels with an alpha value of less than 128 to be fully transparent and not render at all. You can tweak the 128 number if you want the cutoff point to be elsewhere.

### Shadeless materials

If you want to get rid of the the shadows that light sources leave on a mesh, you can make it shadeless.

First find the `"TevStages"` section of the material. It's not the first result when Ctrl+Fing for `"TevStages"`, but the second one - the one under the `"KonstColors"` section. You should see something like this:
```json
    "TevStages": [
      {
        "ColorInA": "C0",
        "ColorInB": "Konst",
        "ColorInC": "TexColor",
        "ColorInD": "Zero",
```
If you want to get rid of the dark shadows on the material so that the whole mesh is evenly lit, change the value of `ColorInC` from `TexColor` to `One`.  
Additionally, if you want ambient lighting color to have no effect on the mesh at all (i.e. so it glows in the dark and night), you can make the material be full bright by changing the value of `ColorInB` from `Konst` to `One`.  
If you change `ColorInB` without changing `ColorInC`, you would get an effect where the shadows still exist normally, but the lit parts that aren't shaded will be full bright.

## Intermediate

### Partial transparency (alpha blending)

Partial transparency (also known as alpha blending) allows meshes to render transparent textures. Unlike [Binary transparency (alpha masking)](#binary-transparency-alpha-masking), partial transparency supports smooth gradients of transparency, although it's a bit more finicky than binary transparency and may sometimes cause things to render strangely if not set up correctly.

Before making the material support transparency, first make sure that the texture itself is set up to support alpha transparency. In tex_headers.json, find the texture for your mesh and look at the `Format` field. The following texture formats support transparency:
* `IA4` (greyscale, 4 bits of alpha)
* `IA8` (greyscale, 8 bits of alpha)
* `RGB5A3` (color, 3 bits of alpha)
* `RGBA32` (color, 8 bits of alpha, large file size)
* `C4` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C8` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `C14X2` (only if `PaletteFormat` is `IA8` or `RGB5A3`)
* `CMPR` (color, 1 bit of alpha)

If the texture doesn't use a format that supports transparency, change it to one that does.  
C8 with the `PaletteFormat` set to `RGB5A3` is generally a good choice as it supports both color and 3 bits of alpha, without making the file size too large.  
Do not use CMPR for partial transparency, as it only supports 1 bit of alpha making it effectively the same as binary transparency.

Next, you can edit the material itself to have partial transparency. To do this, find the part of the material called `"BMode"`, which should also have a section called `"ZMode"` right after it. Replace both of those sections with the following:
```json
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
```json
    "AlphCompare": {
      "Comp0": "Always",
      "Reference0": 0,
      "Operation": "Or",
      "Comp1": "Always",
      "Reference1": 0
    },
```
You don't necessarily have to disable binary transparency if you don't want to - it does work along with partial transparency, it just may give undesired results.

### Modifying TEV Colors and Konst Colors

Each material defines eight colors: four in the `TevColors` section, and another four in the `KonstColors` section. These can be used in TEV Stages.  
Each of the colors will look something like this:
```json
      {
        "R": 1.0,
        "G": 1.0,
        "B": 1.0,
        "A": 1.0
      },
```
R, G, B, and A are short for Red, Green, Blue, and Alpha.  
The values are on a scale from 0.0 to 1.0.  
Many programs that deal with colors on a scale of 0 to 255 instead, so if you're converting a color from another program to the materials.json format, you may have to divide it by 255. For example, the color (64, 149, 153, 255) from another program would convert to:
```json
      {
        "R": 0.25098039215686274509803921568627,
        "G": 0.58431372549019607843137254901961,
        "B": 0.6,
        "A": 1.0
      },
```

The TEV colors work as follows:  
The first and fourth colors in the list cannot be used.  
The second color in the list corresponds to C1 and A1 in the TEV Stages.  
The third color in the list corresponds to C2 and A2 in the TEV Stages.  

The konst colors work as follows:  
Each TEV stage can only access a single konst color.  
The `ColorSels` section defines which color that is for each TEV stage. For example:
```json
    "ColorSels": [
      "KCSel_K0",
      "KCSel_K3",
      "KCSel_K1",
      "KCSel_K3",
      "KCSel_K2",
```
That would mean the following:
* The first TEV stage can access the first konst color (`KCSel_K0`)
* The second TEV stage can access the fourth konst color (`KCSel_K3`)
* The third TEV stage can access the second konst color (`KCSel_K1`)
* The fourth TEV stage can also access the fourth konst color (`KCSel_K3`)
* The fifth TEV stage can access the third konst color (`KCSel_K2`)

### Changing material color

Sometimes, you may want to give a mesh a certain color without editing the color of the texture itself.  
One example is if you want the texture to have a very smooth transparency gradient which requires 8 bits of alpha, but you don't want to use the RGBA32 texture format as it uses up too much file size. In this case, you could use the IA8 texture format which supports 8 bits of alpha, but is greyscale, and then give the material a color to make up for the lack of color in the texture. You would still be limited to only one color, but it could be any color you want, not just grey.  

First, find the `"TevColors"` section of the material, and modify the third color in that section to be whatever color you want the material to be.  

Next, find the `"TevStages"` section of the material. It's not the first result when Ctrl+Fing for `"TevStages"`, but the second one - the one under the `"KonstColors"` section. There may be multiple stages listed in this section, but you want to find the one where `ColorInB` has the value `TexColor`, like so:
```json
      {
        "ColorInA": "Zero",
        "ColorInB": "TexColor",
        "ColorInC": "ColorPrev",
        "ColorInD": "Zero",
```
If you want to completely replace the color of the texture with your material color (e.g. for greyscale textures), change the value of `ColorInB` from `TexColor` to `C2`.  
Alternatively, if you want to keep the texture color and simply tint it with the material color, instead change the value of `ColorInD` from `Zero` to `C2` and leave `ColorInB` alone.

### Removing texture scrolling/scaling

Sometimes, you might edit a model that animates its textures and makes them scroll or scale. If you don't want these animations to apply to your custom model, the easiest way to disable them is to replace the material's texture matrix source with the identity matrix.  

To do this, find the `"Tex1CoordGens"` section of the material, which may look like this:
```json
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

### Custom TEV Stages

TEV stages are the main part of the material, which control exactly what colors and alpha are rendered and how.  
They are listed in the `"TevStages"` section of the material. It's *not* the first result when Ctrl+Fing for `"TevStages"`, but the second one - the one under the `"KonstColors"` section.  
This section has at least one TEV stage in it, but will usually have two or three, and may have up to 16. An example of a single TEV stage is as follows:
```json
      {
        "ColorInA": "C0",
        "ColorInB": "Konst",
        "ColorInC": "TexColor",
        "ColorInD": "Zero",
        "ColorOp": "Add",
        "ColorBias": "Zero",
        "ColorScale": "Scale_1",
        "ColorClamp": true,
        "ColorRegId": "TevPrev",
        "AlphaInA": "Zero",
        "AlphaInB": "Zero",
        "AlphaInC": "Zero",
        "AlphaInD": "Zero",
        "AlphaOp": "Add",
        "AlphaBias": "Zero",
        "AlphaScale": "Scale_1",
        "AlphaClamp": true,
        "AlphaRegId": "TevPrev"
      },
```

`ColorInA`, `ColorInB`, `ColorInC`, and `ColorInD` are the input colors that the TEV stage takes. These are the four most important properties when editing TEV stages.  
`ColorRegId` is what register the TEV stage puts its output color in. This is usually `TevPrev`.  
`ColorOp` is what operation is performed on color D. This is usually `Add`.  
`ColorBias` is what to add to color D. This is usually `Zero`.  
`ColorScale` is what to multiply the output by. This is usually `Scale_1`.  

The formula the TEV stage uses to calculate the output color is as follows:  
`(((1-C)*A + C*B) Op (D + Bias)) * Scale`  
But assuming the usual values for most of those, it can be simplified to the following:  
`((1-C)*A + C*B) + D`  
What this means in plain English is that color C is used to move the output color between A and B, and then D is added at the end. The higher the value of color C, the closer the output will be to color B.  
For example, assuming A is red, B is blue, and D is black:
* C being 0 (black) would output A (red)
* C being 1 (white) would output B (blue)
* C being 0.5 (grey) would output a mix between A and B (purple)

The four color input properties can have the following values:
* `Zero` - Black (0).
* `Half` - Grey (0.5).
* `One` - White (1).
* `TexColor` - The color from the texture.
* `C0` - The color from the first color register, which is always the ambient environmental lighting color from the map.
* `C1` - The color from the second color register, which is the second color in the `TevColors` section.
* `C2` - The color from the third color register, which is the third color in the `TevColors` section.
* `Konst` - One of the four colors from the `KonstColors` section. The `ColorSels` section defines which of the four it is.
* `RasColor` - TODO
* `ColorPrev` - The output color from the previous TEV stage (assuming it output to `TevPrev`).

The alpha properties work basically the same as the color properties, but their values have slightly different names:
* `Zero` - Fully transparent (0).
* `Half` - Half transparent (0.5).
* `One` - Fully opaque (1).
* `TexAlpha` - The alpha from the texture.
* `A0` - The alpha from the first color register, which is always the ambient environmental lighting color from the map.
* `A1` - The alpha from the second color register, which is the second color in the `TevColors` section.
* `A2` - The alpha from the third color register, which is the third color in the `TevColors` section.
* `Konst` - One of the four colors from the `KonstColors` section. The `AlphaSels` section defines which of the four it is.
* `RasAlpha` - TODO
* `AlphaPrev` - The output alpha from the previous TEV stage (assuming it output to `TevPrev`).

### Shiny materials

TODO

### Transparent shiny materials

TODO

### Outlines

TODO

### Vertex colors

TODO

## Other properties

If you want to edit materials in a way not covered in the guide above, you'll have to figure out how by yourself.  
The easiest way to do this is generally to find a material from the vanilla game that already does what you want, and try copying that material (or part of it) over your custom material.  

If what you want to do isn't done in any of the vanilla materials, you'll need to try various things via trial and error to see if you can get the desired effect. There's currently no comprehensive explanation of what all of the dozens of material properties do, so there's no easy way to figure that out.  
However, SuperBMD's source code does have [lists of what possible values of each property can be](https://github.com/LagoLunatic/SuperBMD/tree/master/SuperBMDLib/source/Materials/Enums). For example, `TevOp.cs` lists out the possible values for the `ColorOp` and `AlphaOp` properties of the `TevStages` section - `Add`, `Sub`, etc.  
