"""Mock PicoGraphics module for emulator"""

DISPLAY_COSMIC_UNICORN = 0

class PicoGraphics:
    def __init__(self, display_type):
        self.width = 32
        self.height = 32
        # Initialize pixel buffer with black (0, 0, 0)
        self.pixels = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        self.current_pen = (0, 0, 0)
        self.pens = {}  # Store created pens
        self.font = "bitmap6"

    def get_bounds(self):
        return (self.width, self.height)

    def create_pen(self, r, g, b):
        # Return a unique identifier for this pen
        pen_id = (r, g, b)
        self.pens[pen_id] = (r, g, b)
        return pen_id

    def set_pen(self, pen):
        if pen in self.pens:
            self.current_pen = self.pens[pen]
        else:
            # Assume it's already an RGB tuple
            self.current_pen = pen

    def pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = self.current_pen

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = self.current_pen

    def line(self, x1, y1, x2, y2):
        # Simple line drawing using Bresenham's algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.pixel(x1, y1)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def set_font(self, font):
        self.font = font

    def measure_text(self, text, scale=1):
        # Approximate text width based on font
        if self.font == "bitmap6":
            char_width = 6
        elif self.font == "bitmap14_outline":
            char_width = 8
        else:
            char_width = 6
        return len(text) * char_width * scale

    def text(self, text, x, y, scale=1):
        """Render text with bitmap font patterns"""
        char_width = 6 if self.font == "bitmap6" else 8
        char_height = 6 if self.font == "bitmap6" else 14

        for i, char in enumerate(text):
            char_x = x + (i * char_width * scale)
            bitmap = self._get_char_bitmap(char, char_width, char_height)

            # Draw the character bitmap
            for cy in range(len(bitmap)):
                for cx in range(len(bitmap[cy])):
                    if bitmap[cy][cx]:  # Only draw if pixel is set
                        for sy in range(scale):
                            for sx in range(scale):
                                px = char_x + (cx * scale) + sx
                                py = y + (cy * scale) + sy
                                if 0 <= px < self.width and 0 <= py < self.height:
                                    self.pixels[py][px] = self.current_pen

    def _get_char_bitmap(self, char, width, height):
        """Get a bitmap pattern for a character"""
        from bitmap_font import FONT_5X7

        # Get bitmap from font, case-insensitive
        char_upper = char.upper()
        if char_upper in FONT_5X7:
            return FONT_5X7[char_upper]

        # Default pattern for unknown characters - draw a small box
        return [[1,1,1,1,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,1]]

    def get_pixels(self):
        """Get the current pixel buffer"""
        return self.pixels
