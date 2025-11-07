#!/usr/bin/env python3
"""
Simple test script for the Cosmic Unicorn emulator
This tests basic functionality without requiring API keys.
"""
import sys
import os
import time

# Add emulator mocks to path
emulator_dir = os.path.dirname(os.path.abspath(__file__))
mocks_dir = os.path.join(emulator_dir, 'mocks')
sys.path.insert(0, mocks_dir)
sys.path.insert(0, emulator_dir)

# Import the mock modules
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN
from renderer import get_renderer

def main():
    print("Testing Cosmic Unicorn Emulator...")
    print("=" * 70)

    # Create the display objects
    cosmic = CosmicUnicorn()
    graphics = PicoGraphics(DISPLAY_COSMIC_UNICORN)

    # Get display size
    W, H = graphics.get_bounds()
    print(f"Display size: {W}x{H}")

    # Create some pens
    RED = graphics.create_pen(255, 0, 0)
    GREEN = graphics.create_pen(0, 255, 0)
    BLUE = graphics.create_pen(0, 0, 255)
    BLACK = graphics.create_pen(0, 0, 0)

    # Initialize renderer
    renderer = get_renderer(graphics)
    renderer.start()

    try:
        # Test 1: Clear to black
        print("\nTest 1: Clear to black")
        graphics.set_pen(BLACK)
        graphics.clear()
        cosmic.update(graphics)
        time.sleep(1)

        # Test 2: Draw red horizontal line
        print("Test 2: Red horizontal line")
        graphics.set_pen(RED)
        graphics.line(0, 16, W-1, 16)
        cosmic.update(graphics)
        time.sleep(1)

        # Test 3: Draw green vertical line
        print("Test 3: Green vertical line")
        graphics.set_pen(GREEN)
        graphics.line(16, 0, 16, H-1)
        cosmic.update(graphics)
        time.sleep(1)

        # Test 4: Draw blue border
        print("Test 4: Blue border")
        graphics.set_pen(BLUE)
        for x in range(W):
            graphics.pixel(x, 0)
            graphics.pixel(x, H-1)
        for y in range(H):
            graphics.pixel(0, y)
            graphics.pixel(W-1, y)
        cosmic.update(graphics)
        time.sleep(1)

        # Test 5: Rainbow gradient
        print("Test 5: Rainbow gradient")
        graphics.set_pen(BLACK)
        graphics.clear()
        for x in range(W):
            for y in range(H):
                r = int((x / W) * 255)
                g = int((y / H) * 255)
                b = int(((x + y) / (W + H)) * 255)
                pen = graphics.create_pen(r, g, b)
                graphics.set_pen(pen)
                graphics.pixel(x, y)
        cosmic.update(graphics)
        time.sleep(2)

        print("\n✅ All tests passed!")
        print("Press Ctrl+C to exit...")

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n✋ Test stopped by user")
    finally:
        renderer.stop()

if __name__ == '__main__':
    main()
