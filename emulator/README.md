# Cosmic Unicorn Emulator

A terminal-based emulator for the Pimoroni Cosmic Unicorn LED display board.

## Features

- Displays a 32x32 pixel grid in your terminal using true-color (24-bit RGB)
- Full color fidelity with 16.7 million colors
- Mocks all Cosmic Unicorn hardware modules
- Uses your host machine's network instead of WiFi
- Allows testing and debugging without the physical hardware
- Automatic fallback to ANSI 256-color for older terminals
- All transitions work (fade, wipe, immediate)
- Real-time display updates
- Text rendered using 5x7 bitmap fonts for readability

## Requirements

```bash
pip install requests
```

## Quick Start

### 1. Test the Emulator (No API Keys Required)

Run the emulator with its default test/demo:

```bash
python3 emulator/run_emulator.py
```

This will display:
- A black screen
- A red horizontal line
- A green vertical line
- A blue border
- A rainbow gradient

Press `Ctrl+C` to exit.

### 2. Run Your Office Display

To run the office/main.py application:

```bash
python3 emulator/run_emulator.py office/main.py
```

**Note:** You'll need to edit `office/secrets.py` and add your RapidAPI key for weather data.

### 3. Run Other Applications

```bash
# Run a script in a directory (looks for main.py inside)
python3 emulator/run_emulator.py office/

# Run the Christmas display
python3 emulator/run_emulator.py christmas/

# Run any other Python script
python3 emulator/run_emulator.py examples/demo.py
```

## What You'll See

```
┌────────────────────────────────────────────────────────────────┐
│  [colored blocks representing each pixel]                      │
│  [32 rows of 32 pixels each]                                   │
└────────────────────────────────────────────────────────────────┘

🎮 Cosmic Unicorn Emulator - 32x32 pixels - True Color (24-bit RGB)
Press Ctrl+C to exit
```

## Setup for Applications Requiring API Keys

If running the office application, make sure you have a `secrets.py` file in the `office/` directory with your API keys:

```python
WIFI_SSID = "YourWiFi"  # Not actually used by emulator
WIFI_PASS = "password"  # Not actually used by emulator
RAPIDAPI_KEY = "your-rapidapi-key"
LOCATION = "YourCity"
```

## Command-line Options

```
python3 emulator/run_emulator.py [script]

Arguments:
  script    Python script or directory to run (default: emulator/test_emulator.py)
            - If a directory is specified, looks for main.py inside it
            - If a .py file is specified, runs that file directly
            - Default runs a simple test/demo that requires no API keys
```

## How It Works

The emulator creates a terminal-based 32×32 pixel display using:
- True-color (24-bit RGB) ANSI escape codes for accurate color representation
- Each pixel is rendered as two characters (`  `) with a background color
- Your host machine's network is used instead of WiFi
- All MicroPython hardware modules are mocked

### Mocked Modules

The emulator replaces the following MicroPython modules with Python equivalents:

- `cosmic` - Mocks the CosmicUnicorn class
- `picographics` - Implements a pixel buffer and rendering
- `network` - Uses host network instead of WiFi
- `urequests` - Wraps Python's `requests` library
- `_thread` - Wraps Python's `threading` module
- `machine` - Mocks hardware control (Pin, ADC, PWM, Timer, RTC, etc.)

The terminal renderer converts RGB pixel values to true-color ANSI escape codes and displays them as colored blocks in your terminal, providing full 16.7 million color fidelity.

## Troubleshooting

### "Module 'requests' not found"
```bash
pip3 install requests
```

### "Cannot get weather data"
- Check your `office/secrets.py` file has a valid `RAPIDAPI_KEY`
- The emulator will skip weather display and continue if API fails

### Display looks garbled or colors are wrong
- Make sure your terminal supports true-color (24-bit RGB)
  - **macOS**: Terminal.app (10.12+), iTerm2
  - **Linux**: GNOME Terminal, Konsole, kitty, alacritty
  - **Windows**: Windows Terminal, newer versions of ConEmu
- If your terminal doesn't support true-color, the emulator will fall back to 256-color mode
- Expand your terminal window to at least 80 characters wide

### Images look like solid blocks of color
- This was the old behavior with ANSI 256-color mode
- The emulator now uses true-color by default
- If you're still seeing solid blocks, your terminal may not support true-color
- Try a modern terminal emulator like iTerm2 (macOS) or Windows Terminal

### Text appears as solid blocks
- Make sure you're using the latest version of the emulator
- Text is now rendered using 5x7 bitmap fonts for readability
- If you still see issues, check that bitmap_font.py exists in emulator/mocks/

## Limitations

- Button inputs are not supported (button presses are no-ops)
- Performance may differ from actual hardware
- Some timing might be different
- Requires a terminal that supports true-color (24-bit RGB) for best results
  - Falls back to ANSI 256-color mode on older terminals

## Files

- `emulator/run_emulator.py` - Main emulator runner
- `emulator/test_emulator.py` - Simple test script
- `emulator/renderer.py` - Terminal rendering engine
- `emulator/mocks/` - Mock hardware modules
  - `cosmic.py` - CosmicUnicorn hardware
  - `picographics.py` - Graphics buffer
  - `bitmap_font.py` - 5x7 bitmap font for text rendering
  - `network.py` - Network connectivity
  - `urequests.py` - HTTP requests
  - `_thread.py` - Threading support
  - `machine.py` - Hardware control (Pin, ADC, PWM, etc.)
