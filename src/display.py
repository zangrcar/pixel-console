from __future__ import annotations

from PIL import Image

from src.framebuffer import HEIGHT, WIDTH, FrameBuffer


class Display:
    def __init__(self):
        import board
        import busio
        import adafruit_ssd1306

        i2c = busio.I2C(board.SCL, board.SDA)

        self.display = adafruit_ssd1306.SSD1306_I2C(
            WIDTH,
            HEIGHT,
            i2c,
        )

        self.display.fill(0)
        self.display.show()

    def framebuffer_to_image(self, fb: FrameBuffer) -> Image.Image:
        img = Image.new("1", (WIDTH, HEIGHT), 0)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if fb.pixels[y][x]:
                    img.putpixel((x, y), 1)

        return img

    def show(self, fb: FrameBuffer) -> None:
        img = self.framebuffer_to_image(fb)
        self.display.image(img)
        self.display.show()

    def clear(self) -> None:
        self.display.fill(0)
        self.display.show()