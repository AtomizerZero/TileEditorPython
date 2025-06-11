Basic Tile Editor for CSV map files.

Create an "assets" folder, and drop your tiles into this folder.
Currently, this editor supports individual tiles in png format. "water.png, dirt.png, etc."

In the main file is a dictionary called TILE_TYPES. Add your tiles to this dictionary. 
For example:

TILE_TYPES = {
    0: "empty",
    1: "grass",
    2: "water",
    3: "dirt"
}

CONTROLS:
Mouse: 
    Left click = place tile 
    Right click = remove tile 
    Wheel = zoom

Map: 
    CTRL+Arrows = resize map 
    Arrows = scroll map 
    +/- = zoom in/out

Files: 
    S = save map 
    L = load map 
    CTRL+O = open map
    CTRL+N = new map 
    ESC = quit
        