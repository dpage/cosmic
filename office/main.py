import json
import random
import json
import math
import network
import time
import urequests
import _thread
import gc
import machine
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

PGE_DARK_TEAL = graphics.create_pen(0, 100, 120)
PGE_BASE_TEAL = graphics.create_pen(0, 150, 180)
PGE_LIGHT_TEAL = graphics.create_pen(64, 224, 208)

BLACK = graphics.create_pen(0, 0, 0)
WHITE = graphics.create_pen(255, 255, 255)
RED = graphics.create_pen(255, 0, 0)
GREEN = graphics.create_pen(0, 255, 0)
BLUE = graphics.create_pen(0, 0, 255)
PURPLE = graphics.create_pen(143, 0, 255)
ORANGE = graphics.create_pen(255, 165, 0)

# Global watchdog reference (initialized in main())
wdt = None


def start_wifi():
    if secrets.WIFI_SSID is None or secrets.WIFI_PASS is None:
        raise RuntimeError("WiFi SSID/PASS required. Set them in secrets.py and copy it to your Pico")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)

    # Wait for connection with timeout
    max_wait = 30
    while max_wait > 0 and not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1.0)
        max_wait -= 1
        # Feed watchdog during WiFi connection wait
        if wdt is not None and max_wait % 5 == 0:  # Feed every 5 seconds
            wdt.feed()

    if not wlan.isconnected():
        raise RuntimeError("Failed to connect to WiFi")

    conninfo = 'Connected to {}; IP: {}, mask: {}, router: {}, DNS: {}'.format(
        secrets.WIFI_SSID,
        wlan.ifconfig()[0],
        wlan.ifconfig()[1],
        wlan.ifconfig()[2],
        wlan.ifconfig()[3])

    return wlan, conninfo


def check_and_reconnect_wifi(wlan):
    """Check WiFi connection and reconnect if needed"""
    if not wlan.isconnected():
        print('WiFi disconnected, attempting to reconnect...')
        try:
            wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
            max_wait = 30
            while max_wait > 0 and not wlan.isconnected():
                print('Waiting for reconnection...')
                time.sleep(1.0)
                max_wait -= 1
                # Feed watchdog during WiFi reconnection wait
                if wdt is not None and max_wait % 5 == 0:  # Feed every 5 seconds
                    wdt.feed()

            if wlan.isconnected():
                print('WiFi reconnected successfully')
                return True
            else:
                print('Failed to reconnect to WiFi')
                return False
        except Exception as e:
            print('WiFi reconnection error:', e)
            return False
    return True

def get_weather(wlan):
    """Fetch weather data with proper error handling and timeout"""
    # Check WiFi connection first
    if not check_and_reconnect_wifi(wlan):
        print('Cannot get weather: WiFi not connected')
        return None

    # Feed watchdog before potentially long network operation
    if wdt is not None:
        wdt.feed()

    url = 'https://weatherapi-com.p.rapidapi.com/current.json?q={}'.format(secrets.LOCATION)

    headers = {
        "X-RapidAPI-Key": secrets.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    try:
        # Make request with timeout (keep under watchdog timeout of 8s)
        response = urequests.get(url, headers=headers, timeout=7)

        if response.status_code != 200:
            print('Weather API returned status:', response.status_code)
            response.close()
            return None

        res = json.loads(response.text)
        response.close()
        print('Weather data fetched successfully')
        return res

    except OSError as e:
        print('Network error getting weather:', e)
        return None
    except Exception as e:
        print('Error getting weather:', e)
        return None


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

        # Feed watchdog every column to prevent timeout during long transitions
        if wdt is not None and x % 4 == 0:  # Feed every 4 columns
            wdt.feed()


# Draw an image, given a JSON doc of RGB pixel values
def draw_image(file, transition):
    try:
        f = open(f'images/{file}.json', 'r', encoding='ascii')
        image = json.loads(f.read())
        f.close()
    except Exception as e:
        print(f'Error loading image {file}:', e)
        return  # Skip drawing if image fails to load

    # Clean up memory after loading JSON
    gc.collect()

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

        # Feed watchdog every column to prevent timeout during long transitions
        if wdt is not None and x % 4 == 0:  # Feed every 4 columns
            wdt.feed()


# Render scrolling text, with top and bottom 2-colour borders
def draw_scrolling_text_with_borders(text, text_colour, inner_colour, outer_colour):
    graphics.set_font("bitmap14_outline")
    text_top = int(math.floor(W / 2) - (14 / 2))

    width = graphics.measure_text(text, scale=1)

    scroll_count = 0
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

        # Feed watchdog periodically during long scrolling text
        scroll_count += 1
        if wdt is not None and scroll_count % 50 == 0:  # Feed every 50 frames (~2.5 seconds)
            wdt.feed()
        
        
# Render scrolling text, with a 16x16 icon at the top
def draw_scrolling_text_with_icon(text, text_colour, icon):
    graphics.set_font("bitmap14_outline")
    text_top = H - 14

    width = graphics.measure_text(text, scale=1)

    try:
        f = open(f'icons/{icon}.json', 'r', encoding='ascii')
        image = json.loads(f.read())
        f.close()
    except Exception as e:
        print(f'Error loading icon {icon}:', e)
        return  # Skip drawing if icon fails to load

    # Clean up memory after loading JSON
    gc.collect()

    scroll_count = 0
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

        # Feed watchdog periodically during long scrolling text
        scroll_count += 1
        if wdt is not None and scroll_count % 50 == 0:  # Feed every 50 frames (~2.5 seconds)
            wdt.feed()

    
def main():
    global wdt

    # Initialize watchdog timer - will reset the Pico if not fed within 8 seconds
    # This prevents the display from hanging indefinitely
    # Note: RP2040 WDT max timeout is ~8388ms (8.3 seconds)
    wdt = machine.WDT(timeout=8000)  # 8 second timeout
    print('Watchdog timer initialized (8s timeout)')

    graphics.set_font("bitmap6")
    graphics.set_pen(PURPLE)
    graphics.text('WLAN:', 0, 0, scale=1)

    graphics.set_pen(ORANGE)
    graphics.text(secrets.WIFI_SSID, 0, 8, scale=1)
    cosmic.update(graphics)

    wdt.feed()  # Feed watchdog before network operations

    wlan, conninfo = start_wifi()
    wdt.feed()  # Feed watchdog after WiFi connection

    draw_scrolling_text_with_borders(conninfo, PURPLE, ORANGE, ORANGE)
    clear(FADE)

    last_weather = 0
    weather = None  # Initialize weather to None

    while True:
        # Feed watchdog at the start of each loop iteration
        wdt.feed()

        draw_image('slonik', random_transition())
        wdt.feed()  # Feed after image display

        # Get the weather, or sleep while displaying the first image
        if time.time() > last_weather + 300:
            new_weather = get_weather(wlan)
            wdt.feed()  # Feed after weather fetch
            if new_weather is not None:
                weather = new_weather  # Update only if successful
                last_weather = time.time()
            else:
                print('Failed to get weather, will retry later')
                # Still update last_weather to avoid hammering the API
                last_weather = time.time()
        else:
            time.sleep(2.0)

        clear(random_transition())
        wdt.feed()  # Feed after clear

        draw_scrolling_text_with_borders('PostgreSQL', PG_LIGHT_BLUE, PG_BASE_BLUE, PG_DARK_BLUE)
        wdt.feed()  # Feed after scrolling text
        clear(FADE)

        # Only display weather if we have valid data
        if weather is not None:
            try:
                # General Weather
                draw_scrolling_text_with_icon('Weather for {}: {}'.format(
                    weather['location']['name'],
                    weather['current']['condition']['text']),
                    ORANGE, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
                wdt.feed()  # Feed after weather display

                # Temperature
                draw_scrolling_text_with_icon('Temperature: {}C, feels like: {}C'.format(
                    weather['current']['temp_c'],
                    weather['current']['feelslike_c']),
                    PURPLE, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
                wdt.feed()  # Feed after temperature display

                # Wind
                draw_scrolling_text_with_icon('Wind: {}MPH {}, gusts: {}MPH'.format(
                    weather['current']['wind_mph'],
                    weather['current']['wind_dir'],
                    weather['current']['gust_mph']),
                    GREEN, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
                wdt.feed()  # Feed after wind display

                # Precipitation
                draw_scrolling_text_with_icon('Precipitation: {}mm, UV: {}'.format(
                    weather['current']['precip_mm'],
                    weather['current']['uv']),
                    BLUE, get_weather_icon(weather['current']['condition']['icon'], weather['current']['is_day']))
                wdt.feed()  # Feed after precipitation display
                clear(FADE)
            except Exception as e:
                print('Error displaying weather:', e)
                # Continue with the loop even if weather display fails
        else:
            # No weather data available yet, skip weather display
            print('No weather data available, skipping weather display')

        # Clean up memory after weather display
        gc.collect()
        wdt.feed()  # Feed after garbage collection

        draw_image('pgedge', random_transition())
        wdt.feed()  # Feed after pgEdge image
        time.sleep(2.0)
        clear(random_transition())
        wdt.feed()  # Feed after clear

        draw_scrolling_text_with_borders('pgEdge', PGE_LIGHT_TEAL, PGE_BASE_TEAL, PGE_DARK_TEAL)
        wdt.feed()  # Feed after pgEdge text
        clear(FADE)

        draw_image('pod', random_transition())
        wdt.feed()  # Feed after pod image
        time.sleep(2.0)
        clear(random_transition())
        wdt.feed()  # Feed after clear

        draw_scrolling_text_with_borders('TenaciousDD', TDD_BASE_GREEN, TDD_LIGHT_GREEN, TDD_DARK_GREEN)
        wdt.feed()  # Feed after TenaciousDD text
        clear(FADE)




if __name__ == '__main__':
    main()
