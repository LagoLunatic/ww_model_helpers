
### Table of contents

* [Custom colors](#custom-colors)
* [Color presets](#color-presets)
* [Color masks](#color-masks)
* [Extra metadata.txt options](#extra-metadatatxt-options)

### Custom colors

If you want your model to have custom colors the player can change in the randomizer's UI, you must include a file called metadata.txt in the same folder as Link.arc.  

You can specify what colors there are to change by putting data such as this in your metadata.txt:  
```
hero_custom_colors:
  Color name: 0x98C722
  A different color name: 0x4642C7
casual_custom_colors:
  Yet another color name: 0xC76418
```

The hex color after the color name is what the "base" color for that option is. This is something the randomizer uses when calculating how to recolor the image.  
If the area recolored for a given color option is all a solid color, the base color should simply be that color.  
If the area includes multiple colors you can pick the one that covers the largest amount of the area. The colors you didn't choose might recolor slightly strangely - in this case you can try tweaking the base color or splitting the option into two different color options.  

### Color presets

You can also optionally create color presets that allow the player to select color combinations you choose manually out of a dropdown list in the randomizer's UI:  
```
hero_color_presets:
  A Preset Name:
    Color name: 0x2427C7
    A different color name: 0x52EBC7
  Another Preset Name:
    A different color name: 0xDBEB52
casual_color_presets:
  A Casual Preset Name:
    Yet another color name: 0x361D8A
```
The above creates two presets named "A Preset Name" and "Another Preset Name" for the hero's clothes outfit, and a preset named "A Casual Preset Name" for the casual clothes outfit.  
Note that a preset does not need to specify colors that should be left at the default, base color. In the example above, "Another Preset Name" does not specify a value for "Color name", meaning it will use the default value (98C722, which was specified in hero_custom_colors in the first example).  

### Color masks

Basic color masks for the main linktexS3TC texture should be placed like so (assuming "Color Name" is the name of one of your custom colors):  
```
CustomModelFolder/color_masks/hero_Color Name.png
CustomModelFolder/color_masks/casual_Color Name.png
```
All color options must have a mask for linktexS3TC like this. The only exception is colors that recolor the pupils (see below) - you can still include linktexS3TC masks for pupil colors if you want, but this is not required since you normally wouldn't want linktexS3TC to change with the pupil color.  
<br>

For the player's eyebrow images (mayuh), they are not colorized by default. You can enable this like so:  
```
has_colored_eyebrows: true
```
Furthermore, you can specify which color the texture should be recolored by like so:  
```
hero_eyebrow_color_name: Color Name
casual_eyebrow_color_name: Color Name
```
(These default to "Hair" if not specified.)  
<br>

For the player's casual hair model (katsura), you can specify the color like so:
```
casual_hair_color_name: Color Name
```
(This defaults to "Hair" if not specified.)  
<br>

For the hands.bdl model that contains extra hand poses for the player, you can specify the color like so:  
```
hero_hands_color_name: Color Name
casual_hands_color_name: Color Name
```
(These default to "Skin" if not specified.)  
Alternatively, if recoloring the whole texture doesn't give you enough control, you can make color masks for the hands as well. They should be placed like so:
```
CustomModelFolder/color_masks/hands_hero_Color Name.png
CustomModelFolder/color_masks/hands_casual_Color Name.png
```
(If any hands masks are present, the "hands_color_name" fields above are ignored.)  
<br>

For the player's pupil image (hitomi), you can specify the color like so:
```
hero_hitomi_color_name: Color Name
casual_hitomi_color_name: Color Name
```
(These default to "Eyes" if not specified.)  
Alternatively, you can make color masks for the pupils as well. They should be placed like so:
```
CustomModelFolder/color_masks/hitomi_hero_Color Name.png
CustomModelFolder/color_masks/hitomi_casual_Color Name.png
```
(If any hitomi masks are present, the "hitomi_color_name" fields above are ignored.)  
<br>

For the player's mouth images (mouthS3TC), you can specify the color like so:
```
hero_mouth_color_name: Color Name
casual_mouth_color_name: Color Name
```
(These default to "Skin" if not specified.)  
Alternatively, you can make color masks for the mouths as well. They should be placed like so:
```
CustomModelFolder/color_masks/mouths/mouthS3TC.1_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.2_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.3_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.4_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.5_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.6_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.7_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.8_Color Name.png
CustomModelFolder/color_masks/mouths/mouthS3TC.9_Color Name.png
```
(If any mouth masks are present, the "mouth_color_name" fields above are ignored.)  

### Extra metadata.txt options

You can specify your name and any other notes the player might want to know like so:
```
author: Your name here
comment: Your comment here
```

If you want to prevent the player from using the casual clothes option (e.g. if your model isn't set up to work right in casual mode):
```
disable_casual_clothes: true
```

If you want to change the text that appears next to the "Casual Clothes" checkbox:
```
casual_clothes_option_text: Your custom text here
```

If you want to the ship's sail to be completely invisible (for if your custom ship model shouldn't have a sail on it):
```
hide_ship_sail: true
```
