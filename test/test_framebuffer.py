from src.framebuffer import FrameBuffer

def test_framebuffer():
    fb = FrameBuffer()
    fb.clear(0)
    fb.rect(0, 0, 128, 64)
    fb.frect(10, 10, 20, 10)
    fb.save_png("output/test.png")