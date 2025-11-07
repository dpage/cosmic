"""Terminal renderer for Cosmic Unicorn emulator"""
import sys
import time

class TerminalRenderer:
    def __init__(self, graphics):
        self.graphics = graphics
        self.last_render_time = 0
        self.min_frame_time = 0.033  # ~30 FPS max

    def rgb_to_ansi256(self, r, g, b):
        """Convert RGB to ANSI 256 color code"""
        # If it's a grayscale color
        if r == g == b:
            if r < 8:
                return 16
            if r > 248:
                return 231
            return round(((r - 8) / 247) * 24) + 232

        # Otherwise, use the 6x6x6 color cube
        r_idx = round(r / 255 * 5)
        g_idx = round(g / 255 * 5)
        b_idx = round(b / 255 * 5)
        return 16 + 36 * r_idx + 6 * g_idx + b_idx

    def clear_screen(self):
        """Clear terminal screen"""
        print('\033[2J\033[H', end='')

    def render(self, use_truecolor=True):
        """Render the current graphics buffer to terminal

        Args:
            use_truecolor: If True, use 24-bit RGB colors. If False, use ANSI 256 colors.
        """
        # Throttle rendering
        current_time = time.time()
        if current_time - self.last_render_time < self.min_frame_time:
            return
        self.last_render_time = current_time

        # Move cursor to home position
        print('\033[H', end='')

        pixels = self.graphics.get_pixels()
        width, height = self.graphics.get_bounds()

        # Draw top border
        print('┌' + '─' * (width * 2) + '┐')

        # Render each row
        for y in range(height):
            print('│', end='')
            for x in range(width):
                r, g, b = pixels[y][x]
                if use_truecolor:
                    # Use 24-bit RGB (true color) - supported by most modern terminals
                    print(f'\033[48;2;{r};{g};{b}m  \033[0m', end='')
                else:
                    # Use ANSI 256 color palette (fallback)
                    color_code = self.rgb_to_ansi256(r, g, b)
                    print(f'\033[48;5;{color_code}m  \033[0m', end='')
            print('│')

        # Draw bottom border
        print('└' + '─' * (width * 2) + '┘')

        # Show some info
        color_mode = "True Color (24-bit RGB)" if use_truecolor else "ANSI 256-color"
        print(f'\n🎮 Cosmic Unicorn Emulator - {width}x{height} pixels - {color_mode}')
        print('Press Ctrl+C to exit\n')

        sys.stdout.flush()

    def start(self):
        """Initialize terminal for rendering"""
        # Clear screen and hide cursor
        self.clear_screen()
        print('\033[?25l', end='')  # Hide cursor
        sys.stdout.flush()

    def stop(self):
        """Restore terminal state"""
        print('\033[?25h', end='')  # Show cursor
        print('\033[0m')  # Reset colors
        sys.stdout.flush()


# Global renderer instance
_renderer = None

def get_renderer(graphics=None):
    """Get or create the global renderer instance"""
    global _renderer
    if _renderer is None and graphics is not None:
        _renderer = TerminalRenderer(graphics)
    return _renderer
