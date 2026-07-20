from PIL import Image

from src.font import encode_text, get_font

WIDTH = 128
HEIGHT = 64

class FrameBuffer:
    def __init__(self):
        self.pixels = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        
    def clear(self, color=0):
        color = 1 if color else 0
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.pixels[y][x]=color
                
    def pset(self, x, y, mode=1):
        if not (0<=x<WIDTH and 0<=y<HEIGHT):
            return
        
        if mode == 0:
            self.pixels[y][x] = 0
        elif mode == 1:
            self.pixels[y][x] = 1
        elif mode == 2:
            self.pixels[y][x] ^= 1
        elif mode == 3:
            self.pixels[y][x] ^= 1
        else:
            raise ValueError(f"Invalid draw mode: {mode}")
        
    def rect(self, x, y, w, h, mode=1):
        for px in range(x, x + w):
            self.pset(px, y, mode)
            self.pset(px, y + h - 1, mode)

        for py in range(y, y + h):
            self.pset(x, py, mode)
            self.pset(x + w - 1, py, mode)

    def frect(self, x, y, w, h, mode=1):
        for py in range(y, y + h):
            for px in range(x, x + w):
                self.pset(px, py, mode)
                
    def displayText(self, x, y, text, mode=1, font_id=0, scale=1):
        if isinstance(text, str):
            data = encode_text(text, replace_unknown=True)
        else:
            data = bytes(text)

        font = get_font(font_id)

        if not 1 <= scale <= 4:
            raise ValueError(f"Invalid font scale: {scale}")

        start_x = x
        cursor_x = x
        cursor_y = y
        fallback = font.glyphs[ord("?")]

        for byte in data:
            if byte == 0x0A:
                cursor_x = start_x
                cursor_y += (font.height + font.line_spacing) * scale
                continue

            glyph = font.glyphs.get(byte, fallback)

            for glyph_y, row in enumerate(glyph):
                for glyph_x in range(font.width):
                    bit = 1 << (font.width - glyph_x - 1)

                    if not row & bit:
                        continue

                    pixel_x = cursor_x + glyph_x * scale
                    pixel_y = cursor_y + glyph_y * scale

                    for scale_y in range(scale):
                        for scale_x in range(scale):
                            self.pset(pixel_x + scale_x, pixel_y + scale_y, mode)

            cursor_x += (font.width + font.spacing) * scale
        
    def line(self, x0, y0, x1, y1, mode=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:
            self.pset(x0, y0, mode)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy
                
    def sprite(self, x, y, sprite, frame=0, mode=1):
        if frame < 0 or frame >= sprite.frame_count:
            raise ValueError("Invalid sprite frame")

        data = sprite.frames[frame]
        bytes_per_row = (sprite.width + 7) // 8

        for row in range(sprite.height):
            for col in range(sprite.width):
                byte_index = row * bytes_per_row + (col // 8)
                bit_index = 7 - (col % 8)

                byte = data[byte_index]

                if byte & (1 << bit_index):
                    self.pset(x + col, y + row, mode)
        
    
    def save_png(self, path, scale=4):
        img = Image.new("1", (WIDTH, HEIGHT), 0)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.pixels[y][x]:
                    img.putpixel((x, y), 1)

        img = img.resize((WIDTH * scale, HEIGHT * scale))
        img.save(path)
        
    def copy(self):
        other = FrameBuffer()
        other.pixels = [row[:] for row in self.pixels]
        return other
