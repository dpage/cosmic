"""Mock Cosmic Unicorn module for emulator"""

class CosmicUnicorn:
    SWITCH_BRIGHTNESS_UP = 0
    SWITCH_BRIGHTNESS_DOWN = 1

    def __init__(self):
        self.brightness = 0.75
        self.pressed_buttons = set()

    def set_brightness(self, brightness):
        self.brightness = max(0.0, min(1.0, brightness))

    def is_pressed(self, button):
        # In emulator, buttons are not pressed
        return False

    def update(self, graphics):
        # Trigger rendering when display is updated
        try:
            import sys
            import os
            # Add emulator directory to path
            emulator_path = os.path.join(os.path.dirname(__file__), '..')
            if emulator_path not in sys.path:
                sys.path.insert(0, emulator_path)

            from renderer import get_renderer
            renderer = get_renderer(graphics)
            if renderer:
                renderer.render()
        except Exception as e:
            # Fail silently if renderer not available
            pass
