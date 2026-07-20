from __future__ import annotations

from PIL import Image

from src.framebuffer import HEIGHT, WIDTH, FrameBuffer


class DisplayError(Exception):
    pass


class Display:
    def __init__(self):
        try:
            from src.vendor.waveshare_OLED import OLED_2in42

            self.display = OLED_2in42.OLED_2in42()
            result = self.display.Init()

            if result not in (None, 0):
                raise RuntimeError(f"Waveshare Init returned {result}")

            actual_size = (self.display.width, self.display.height)
            expected_size = (WIDTH, HEIGHT)

            if actual_size != expected_size:
                raise ValueError(
                    f"Expected display size {expected_size}, got {actual_size}"
                )

            self.display.clear()
        except Exception as error:
            raise DisplayError("Failed to initialize Waveshare OLED_2in42 SSD1309") from error

    @staticmethod
    def framebuffer_to_image(fb: FrameBuffer) -> Image.Image:
        # The Waveshare driver treats black source pixels as lit OLED pixels:
        # getbuffer() clears their bits and ShowImage() inverts those bits again.
        image = Image.new("1", (WIDTH, HEIGHT), 1)

        image.putdata([
            0 if pixel else 255
            for row in fb.pixels
            for pixel in row
        ])

        return image

    def show(self, fb: FrameBuffer) -> None:
        try:
            image = self.framebuffer_to_image(fb)
            buffer = self.display.getbuffer(image)
            self.display.ShowImage(buffer)
        except Exception as error:
            raise DisplayError("Failed to show SSD1309 OLED frame") from error

    def clear(self) -> None:
        try:
            self.display.clear()
        except Exception as error:
            raise DisplayError("Failed to clear SSD1309 OLED") from error

    def blank(self) -> None:
        self.clear()
