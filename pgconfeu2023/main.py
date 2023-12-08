import json
import time
import machine
import math
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

# Create Cosmic object and graphics surface for drawing
cosmic = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)

# Default brightness
brightness = 0.75
cosmic.set_brightness(brightness)
graphics.clear()

# Get the display size
W, H = graphics.get_bounds()

# Fancy rendering directions
LEFT_TO_RIGHT = 1
TOP_TO_BOTTOM = 2
RIGHT_TO_LEFT = 3
BOTTOM_TO_TOP = 4
IMMEDIATE = 5
FADE = 6

# Colours
PG_DARK_BLUE = graphics.create_pen(0, 100, 165)
PG_BASE_BLUE = graphics.create_pen(51, 103, 145)
PG_LIGHT_BLUE = graphics.create_pen(0, 139, 185)

PGCONFEU_LIGHT_BROWN = graphics.create_pen(219, 153, 73)
PGCONFEU_MID_BROWN = graphics.create_pen(157, 95, 24)
PGCONFEU_DARK_BROWN = graphics.create_pen(102, 65, 19)

CZ_RED = graphics.create_pen(215, 20, 26)
CZ_BLUE = graphics.create_pen(17, 69, 126)

BLACK = graphics.create_pen(0, 0, 0)
WHITE = graphics.create_pen(255, 255, 255)


# Interpolate between two numbers
def interpolate(start, stop, steps):
    if steps == 1:
        return [start]
    return [start+(stop-start)/(steps-1)*i for i in range(steps)]


# Handle button presses
# TODO: Figure out how to de-bounce
def buttons():
    global brightness
    
    if cosmic.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        brightness += 0.01
        brightness = min(brightness, 1.0)
        cosmic.set_brightness(brightness)
        time.sleep(0.01)

    if cosmic.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        brightness -= 0.01
        brightness = max(brightness, 0.0)
        cosmic.set_brightness(brightness) 
        time.sleep(0.01)


# Clear the display in various ways
def clear(mode):
    global brightness
    
    if mode == IMMEDIATE:
        graphics.clear()
        cosmic.update(graphics)
        return
    
    elif mode == FADE:
        for b in interpolate(brightness, 0, 20):
            cosmic.set_brightness(b) 
            cosmic.update(graphics)
            time.sleep(0.05)
            
        graphics.clear()
        cosmic.set_brightness(brightness) 
        cosmic.update(graphics)
        return        
        
    elif mode in [LEFT_TO_RIGHT, TOP_TO_BOTTOM]:
        x_range = range(0, W - 1)
        y_range = range(0, H - 1)
        
    elif mode in [RIGHT_TO_LEFT, BOTTOM_TO_TOP]:
        x_range = range(W - 1, -1, -1)
        y_range = range(H - 1, -1, -1)
        
    else:
        raise Exception('Invalid direction specified.')

    for x in x_range:
        for y in y_range:
            if mode in [LEFT_TO_RIGHT, RIGHT_TO_LEFT]:
                graphics.pixel(x, y)
            else:
                graphics.pixel(y, x)
            
            buttons()

            cosmic.update(graphics)


# Draw an image, given a JSON doc of RGB pixel values
def draw_image(file, mode):
    f = open(f'images/{file}.json', 'r', encoding='ascii')
    image = json.loads(f.read())
    f.close()
    
    if mode == IMMEDIATE:
        for y in range(0, H - 1):
            for x in range(0, W - 1):
                colour = graphics.create_pen(image[y][x][0], image[y][x][1], image[y][x][2])
                graphics.set_pen(colour)
                graphics.pixel(x, y)
                
        buttons()

        cosmic.update(graphics)
        return
    elif mode in [LEFT_TO_RIGHT, TOP_TO_BOTTOM]:
        x_range = range(0, W - 1)
        y_range = range(0, H - 1)
    elif mode in [RIGHT_TO_LEFT, BOTTOM_TO_TOP]:
        x_range = range(W - 1, -1, -1)
        y_range = range(H - 1, -1, -1)
    else:
        raise Exception('Invalid direction specified.')
    
    for x in x_range:
        for y in y_range:
            if mode in [LEFT_TO_RIGHT, RIGHT_TO_LEFT]:
                colour = graphics.create_pen(image[y][x][0], image[y][x][1], image[y][x][2])
                graphics.set_pen(colour)
                graphics.pixel(x, y)
            else:
                colour = graphics.create_pen(image[x][y][0], image[x][y][1], image[x][y][2])
                graphics.set_pen(colour)
                graphics.pixel(y, x)
                
            buttons()

            cosmic.update(graphics)
            

# Render scrolling text, with top and bottom 2-colour borders
def draw_scrolling_text(text, text_colour, inner_colour, outer_colour):
    black = graphics.create_pen(0, 0, 0)
    
    graphics.set_font("bitmap14_outline")
    text_top = int(math.floor(W/2) - (14/2))
    
    width = graphics.measure_text(text, scale=1)
    
    for x in range(W, -(width), -1):
        graphics.clear()
        
        graphics.set_pen(outer_colour)
        graphics.line(0, 0, W, 0)
        graphics.set_pen(inner_colour)
        graphics.line(0, 1, W, 1)

        graphics.set_pen(text_colour)
        graphics.text(text, x, text_top, scale=1)

        graphics.set_pen(inner_colour)
        graphics.line(0, H-2, W, H-2)
        graphics.set_pen(outer_colour)
        graphics.line(0, H-1, W, H-1)
    
        graphics.set_pen(black)
        
        buttons()
        
        cosmic.update(graphics)
        
        time.sleep(0.1)
        

while True:
    draw_image('slonik', LEFT_TO_RIGHT)
    time.sleep(2.0)
    clear(LEFT_TO_RIGHT)

    draw_scrolling_text('PGConf.EU 2023', PG_LIGHT_BLUE, PG_BASE_BLUE, PG_DARK_BLUE)
    clear(FADE)

    draw_image('pgconfeu', TOP_TO_BOTTOM)
    time.sleep(2.0)
    clear(TOP_TO_BOTTOM)
    
    
    draw_scrolling_text('The world\'s most advanced database conference', PGCONFEU_LIGHT_BROWN, PGCONFEU_MID_BROWN, PGCONFEU_DARK_BROWN)
    clear(FADE)
    
    draw_image('czech_flag', BOTTOM_TO_TOP)
    time.sleep(2.0)
    clear(BOTTOM_TO_TOP)

    draw_scrolling_text('Prague, Czechia', WHITE, CZ_BLUE, CZ_RED)
    clear(FADE)
