import json
import random
import json 
import math
import network
import time
import urequests
import _thread
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
import socket

import secrets

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
RED = graphics.create_pen(255, 0, 0)
GREEN = graphics.create_pen(0, 255, 0)
BLUE = graphics.create_pen(0, 0, 255)
PURPLE = graphics.create_pen(143, 0, 255)
ORANGE = graphics.create_pen(255, 165, 0)


def start_wifi():
    if secrets.WIFI_SSID is None or secrets.WIFI_PASS is None:
        raise RuntimeError("WiFi SSID/PASS required. Set them in secrets.py and copy it to your Pico")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1.0)

    print('Connected to {}; IP: {}, mask: {}, router: {}, DNS: {}'.format(secrets.WIFI_SSID,
                                                                          wlan.ifconfig()[0],
                                                                          wlan.ifconfig()[1],
                                                                          wlan.ifconfig()[2],
                                                                          wlan.ifconfig()[3]))

def get_weather():
    url = 'https://weatherapi-com.p.rapidapi.com/current.json?q={}'.format(secrets.LOCATION)

    headers = {
        "X-RapidAPI-Key": secrets.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    response = urequests.get(url, headers=headers)
        
    res = json.loads(response.text)
    response.close()

    return res


def get_weather_icon(url, is_day):
    file = url.split('/')[-1]
    file = file.split('.')[0]
    
    if is_day == 1:
        return 'day/{}'.format(file)
    else:
        return 'night/{}'.format(file)
    
    
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
def draw_scrolling_text_with_borders(text, text_colour, inner_colour, outer_colour):
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
        
        
# Render scrolling text, with a 16x16 icon at the top
def draw_scrolling_text_with_icon(text, text_colour, icon):
    graphics.set_font("bitmap14_outline")
    text_top = H - 14

    width = graphics.measure_text(text, scale=1)

    f = open(f'icons/{icon}.json', 'r', encoding='ascii')
    image = json.loads(f.read())
    f.close()
    
    for x in range(W, -(width), -1):
        graphics.clear()
        
        for iy in range(0, 16):
            for ix in range(0, 16):
                colour = graphics.create_pen(image[iy][ix][0], image[iy][ix][1], image[iy][ix][2])
                graphics.set_pen(colour)
                graphics.pixel(ix + math.floor(W / 4), iy)

        graphics.set_pen(text_colour)
        graphics.text(text, x, text_top, scale=1)

        graphics.set_pen(BLACK)

        cosmic.update(graphics)
        buttons()

        time.sleep(0.05)

    
def main():
    start_wifi()

    last_weather = 0;
    
    while True:
        draw_image('slonik', random_transition())
        
        # Get the weather, or sleep while displaying the first image
        if time.time() > last_weather + 300:
            weather = get_weather()
            last_weather = time.time()
        else:
            time.sleep(2.0)
            
        clear(random_transition())

        draw_scrolling_text_with_borders('PostgreSQL', PG_LIGHT_BLUE, PG_BASE_BLUE, PG_DARK_BLUE)
        clear(FADE)
        
        # General Weather
        draw_scrolling_text_with_icon('Weather for {}: {}'.format(
            weather['location']['name'],
            weather['current']['condition']['text']),
            ORANGE, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))

        # Temperature
        draw_scrolling_text_with_icon('Temperature: {}C, feels like: {}C'.format(
            weather['current']['temp_c'],
            weather['current']['feelslike_c']),
            PURPLE, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
        
        # Wind
        draw_scrolling_text_with_icon('Wind: {}MPH {}, gusts: {}MPH'.format(
            weather['current']['wind_mph'],
            weather['current']['wind_dir'],
            weather['current']['gust_mph']),
            GREEN, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
        
        # Precipitation
        draw_scrolling_text_with_icon('Precipitation: {}mm, UV: {}'.format(
            weather['current']['precip_mm'],
            weather['current']['uv']),
            BLUE, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
        clear(FADE)

        draw_image('pod', random_transition())
        time.sleep(2.0)
        clear(random_transition())

        draw_scrolling_text_with_borders('TenaciousDD', TDD_BASE_GREEN, TDD_LIGHT_GREEN, TDD_DARK_GREEN)
        clear(FADE)




if __name__ == '__main__':
    main()
