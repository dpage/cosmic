# Cosmic Unicorn

Random code for Pinorami's Cosmic Unicorn display 
(https://shop.pimoroni.com/products/space-unicorns?variant=40842626596947).

## convert_image.py

This is an extremely quick hack of code to convert a directory of images 
into a 32x32 image, expressed in JSON as a grid of RGB values. This allows 
us to easily render whatever parts of the image we want, or to render it 
pixel by pixel or whatever, to give a nice effect.

### TODO

* Make this into a more usable command line tool
* Improve the JSON format to save space, perhaps by generating a palette, and
   referencing entries in that from the pixel matrix.

## pgconfeu2023/

This directory contains the MicroPython code and JSON formatted images for 
presentation on the PGEU desk at PostgreSQL Conference Europe 2023.

The code contains some useful functions for clearing the screen and display
images and text in interesting ways.

### TODO

* Move the fun parts out into a separate module for reuse in other projects.

# Handy Links

* [Cosmic Unicorn documentation](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/cosmic_unicorn/)
* [Pico Graphics documentation](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics)
* [Galactic Unicorn: Multiverse](https://github.com/Gadgetoid/gu-multiverse) (for driving multiple displays from a controller system)
