import sys
from types import ModuleType

import pytest

from src.display import Display, DisplayError
from src.error_screen import ERRORS, classify_error
from src.framebuffer import FrameBuffer, HEIGHT, WIDTH


class FakeWaveshareDriver:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.expected_width = width
        self.expected_height = height
        self.init_calls = 0
        self.clear_calls = 0
        self.buffers = []
        self.images = []
        self.fail_init = False
        self.fail_clear = False
        self.fail_buffer = False
        self.fail_show = False
        self.init_result = None

    def Init(self):
        if self.fail_init:
            raise OSError("SPI init failed")
        self.init_calls += 1
        self.width = self.expected_width
        self.height = self.expected_height
        return self.init_result

    def clear(self):
        if self.fail_clear:
            raise OSError("clear failed")
        self.clear_calls += 1

    def getbuffer(self, image):
        if self.fail_buffer:
            raise OSError("buffer conversion failed")
        self.images.append(image)
        return b"waveshare-buffer"

    def ShowImage(self, buffer):
        if self.fail_show:
            raise OSError("SPI write failed")
        self.buffers.append(buffer)


def display_with_driver(driver):
    display = object.__new__(Display)
    display.display = driver
    return display


def install_fake_waveshare_module(monkeypatch, driver):
    package = ModuleType("src.vendor.waveshare_OLED")
    module = ModuleType("src.vendor.waveshare_OLED.OLED_2in42")
    module.OLED_2in42 = lambda: driver
    package.OLED_2in42 = module
    monkeypatch.setitem(sys.modules, "src.vendor.waveshare_OLED", package)
    monkeypatch.setitem(sys.modules, "src.vendor.waveshare_OLED.OLED_2in42", module)


def test_ssd1309_initialization_uses_official_waveshare_driver(monkeypatch):
    driver = FakeWaveshareDriver()
    install_fake_waveshare_module(monkeypatch, driver)

    display = Display()

    assert display.display is driver
    assert driver.init_calls == 1
    assert driver.clear_calls == 1


def test_wrong_waveshare_display_dimensions_are_rejected(monkeypatch):
    driver = FakeWaveshareDriver(width=128, height=32)
    install_fake_waveshare_module(monkeypatch, driver)

    with pytest.raises(DisplayError, match="OLED_2in42 SSD1309"):
        Display()


def test_initialization_failure_becomes_display_error(monkeypatch):
    driver = FakeWaveshareDriver()
    driver.fail_init = True
    install_fake_waveshare_module(monkeypatch, driver)

    with pytest.raises(DisplayError, match="initialize Waveshare"):
        Display()


def test_negative_waveshare_init_result_is_rejected(monkeypatch):
    driver = FakeWaveshareDriver()
    driver.init_result = -1
    install_fake_waveshare_module(monkeypatch, driver)

    with pytest.raises(DisplayError, match="initialize Waveshare"):
        Display()


def test_framebuffer_is_converted_to_monochrome_pillow_image():
    framebuffer = FrameBuffer()
    framebuffer.pset(0, 0)
    framebuffer.pset(127, 63)

    image = display_with_driver(FakeWaveshareDriver()).framebuffer_to_image(framebuffer)

    assert image.mode == "1"
    assert image.size == (WIDTH, HEIGHT)
    # OLED_2in42.getbuffer() and ShowImage() expect black artwork on white.
    assert image.getpixel((0, 0)) == 0
    assert image.getpixel((127, 63)) == 0
    assert image.getpixel((1, 1)) != 0


def test_show_uses_waveshare_getbuffer_and_showimage():
    driver = FakeWaveshareDriver()
    display = display_with_driver(driver)
    framebuffer = FrameBuffer()
    framebuffer.pset(4, 5)

    display.show(framebuffer)

    assert len(driver.images) == 1
    assert driver.images[0].getpixel((4, 5)) == 0
    assert driver.images[0].getpixel((5, 5)) != 0
    assert driver.buffers == [b"waveshare-buffer"]


@pytest.mark.parametrize("method", ["clear", "blank"])
def test_clear_and_blank_use_official_driver_clear(method):
    driver = FakeWaveshareDriver()
    display = display_with_driver(driver)

    getattr(display, method)()

    assert driver.clear_calls == 1


@pytest.mark.parametrize(
    "method, failure, message",
    [
        ("show", "fail_buffer", "show SSD1309 OLED frame"),
        ("show", "fail_show", "show SSD1309 OLED frame"),
        ("clear", "fail_clear", "clear SSD1309 OLED"),
        ("blank", "fail_clear", "clear SSD1309 OLED"),
    ],
)
def test_driver_failures_become_controlled_display_errors(method, failure, message):
    driver = FakeWaveshareDriver()
    setattr(driver, failure, True)
    display = display_with_driver(driver)

    with pytest.raises(DisplayError, match=message):
        if method == "show":
            display.show(FrameBuffer())
        else:
            getattr(display, method)()


def test_display_error_maps_to_specific_oled_code():
    assert classify_error(DisplayError("private detail")) == ERRORS["ERR 20"]
