# map_tiles

This is just a simple program that creates a familiar tiled map in a window.

I've seen others employ custom methods for this, but basically it seems that the
*.atlas file is the way that Kivy officially supports tiles.  So we are doing it
that way.

The Kivy atlas seems pretty easy to use, but it would be nice if it would support
indexed arrays of tiles in a more general way.  It would be nice if I could just
define a tile size (h, w), and maybe an optional padding value, and have it just
auto-index an array of tiles based on the source image's available dimensions. 
