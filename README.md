# Cosmic Unicorn

Random code for Pinorami's Cosmic Unicorn display 
(https://shop.pimoroni.com/products/space-unicorns?variant=40842626596947).

## convert_image.py

This is an extremely quick hack of code to convert a PNG file (or other 
formats if the code is tweaked) into a 32x32 image, expressed in JSON as a 
grid of RGB values. This allows us to easily render whatever parts of the 
image we want, or to render it pixel by pixel or whatever, to give a nice
effect.

TODO: Make this into a more usable command line tool!

## pgconfeu2023/

This directory contains the MicroPython code and JSON formatted images for 
presentation on the PGEU desk at PostgreSQL Conference Europe 2023.

The code contains some useful functions for clearing the screen and display
images and text in interesting ways.

TODO: Move the fun parts out into a separate module for reuse in other projects.