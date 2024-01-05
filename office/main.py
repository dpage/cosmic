import json
import random
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

# Fancy rendering transitions
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

TDD_DARK_GREEN = graphics.create_pen(28, 119, 62)
TDD_BASE_GREEN = graphics.create_pen(39, 190, 107)
TDD_LIGHT_GREEN = graphics.create_pen(95, 215, 162)

BLACK = graphics.create_pen(0, 0, 0)
WHITE = graphics.create_pen(255, 255, 255)


# Get a random transition
def random_transition():
    return random.randint(1, 6)


# Interpolate between two numbers
def interpolate(start, stop, steps):
    if steps == 1:
        return [start]
    return [start + (stop - start) / (steps - 1) * i for i in range(steps)]


# Handle button presses
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
def clear(transition):
    global brightness

    graphics.set_pen(BLACK)

    if transition == IMMEDIATE:
        graphics.clear()
        cosmic.update(graphics)
        buttons()
        return

    elif transition == FADE:
        for b in interpolate(brightness, 0, 20):
            cosmic.set_brightness(b)
            cosmic.update(graphics)
            time.sleep(0.05)

        graphics.clear()
        cosmic.set_brightness(brightness)
        cosmic.update(graphics)
        buttons()
        return

    elif transition in [LEFT_TO_RIGHT, TOP_TO_BOTTOM]:
        x_range = range(0, W)
        y_range = range(0, H)

    elif transition in [RIGHT_TO_LEFT, BOTTOM_TO_TOP]:
        x_range = range(W - 1, -1, -1)
        y_range = range(H - 1, -1, -1)

    else:
        raise Exception('Invalid transition specified.')

    for x in x_range:
        for y in y_range:
            if transition in [LEFT_TO_RIGHT, RIGHT_TO_LEFT]:
                graphics.pixel(x, y)
            else:
                graphics.pixel(y, x)

            cosmic.update(graphics)
            buttons()


# Draw an image, given a JSON doc of RGB pixel values
def draw_image(file, transition):
    f = open(f'images/{file}.json', 'r', encoding='ascii')
    image = json.loads(f.read())
    f.close()

    if transition == FADE:
        cosmic.set_brightness(0)
        graphics.clear()
        cosmic.update(graphics)

        for y in range(0, H):
            for x in range(0, W):
                colour = graphics.create_pen(image[y][x][0], image[y][x][1], image[y][x][2])
                graphics.set_pen(colour)
                graphics.pixel(x, y)

        for b in interpolate(0, brightness, 20):
            cosmic.set_brightness(b)
            cosmic.update(graphics)
            buttons()
            time.sleep(0.05)

        return

    elif transition == IMMEDIATE:
        for y in range(0, H):
            for x in range(0, W):
                colour = graphics.create_pen(image[y][x][0], image[y][x][1], image[y][x][2])
                graphics.set_pen(colour)
                graphics.pixel(x, y)

        cosmic.update(graphics)
        buttons()
        return

    elif transition in [LEFT_TO_RIGHT, TOP_TO_BOTTOM]:
        x_range = range(0, W)
        y_range = range(0, H)

    elif transition in [RIGHT_TO_LEFT, BOTTOM_TO_TOP]:
        x_range = range(W - 1, -1, -1)
        y_range = range(H - 1, -1, -1)

    else:
        raise Exception('Invalid transition specified.')

    for x in x_range:
        for y in y_range:
            if transition in [LEFT_TO_RIGHT, RIGHT_TO_LEFT]:
                colour = graphics.create_pen(image[y][x][0], image[y][x][1], image[y][x][2])
                graphics.set_pen(colour)
                graphics.pixel(x, y)
            else:
                colour = graphics.create_pen(image[x][y][0], image[x][y][1], image[x][y][2])
                graphics.set_pen(colour)
                graphics.pixel(y, x)

            cosmic.update(graphics)
            buttons()


# Render scrolling text, with top and bottom 2-colour borders
def draw_scrolling_text(text, text_colour, inner_colour, outer_colour):
    graphics.set_font("bitmap14_outline")
    text_top = int(math.floor(W / 2) - (14 / 2))

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
        graphics.line(0, H - 2, W, H - 2)
        graphics.set_pen(outer_colour)
        graphics.line(0, H - 1, W, H - 1)

        graphics.set_pen(BLACK)

        cosmic.update(graphics)
        buttons()

        time.sleep(0.05)


while True:
    draw_image('slonik', random_transition())
    time.sleep(2.0)
    clear(random_transition())

    draw_scrolling_text('PostgreSQL', PG_LIGHT_BLUE, PG_BASE_BLUE, PG_DARK_BLUE)
    clear(FADE)
    
    draw_image('pod', random_transition())
    time.sleep(2.0)
    clear(random_transition())
    
    draw_scrolling_text('TenaciousDD', TDD_BASE_GREEN, TDD_LIGHT_GREEN, TDD_DARK_GREEN)
    clear(FADE)
