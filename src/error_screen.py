from __future__ import annotations

from src.framebuffer import FrameBuffer


def make_error_frame(code: str, message: str = "") -> FrameBuffer:
    fb = FrameBuffer()
    fb.clear(0)

    fb.displayText(4, 6, "CARD ERROR", 1)
    fb.displayText(4, 22, code[:18], 1)

    if message:
        fb.displayText(4, 38, message[:18], 1)

    return fb


def show_error(display, code: str, message: str = "") -> None:
    fb = make_error_frame(code, message)
    display.show(fb)