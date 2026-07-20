import pytest

from src.font import FONTS, SLOVENIAN_BYTES, get_font
from src.framebuffer import FrameBuffer


REQUIRED_ASCII = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,!?#:;-_'\"()/+=<>"
)


def pixels(framebuffer):
    return tuple(tuple(row) for row in framebuffer.pixels)


def test_five_fonts_have_complete_required_glyph_sets():
    required = {ord(char) for char in REQUIRED_ASCII} | set(SLOVENIAN_BYTES)

    assert set(FONTS) == set(range(5))
    assert [FONTS[font_id].name for font_id in range(5)] == [
        "Classic",
        "Tall",
        "Wide",
        "Italic",
        "Bold",
    ]

    for font in FONTS.values():
        assert required <= set(font.glyphs)
        assert all(len(rows) == font.height for rows in font.glyphs.values())
        assert all(row.bit_length() <= font.width for rows in font.glyphs.values() for row in rows)


def test_all_five_font_styles_render_differently():
    rendered = []

    for font_id in range(5):
        fb = FrameBuffer()
        fb.displayText(0, 0, b"Ab3?\x80\x83", font_id=font_id)
        rendered.append(pixels(fb))

    assert len(set(rendered)) == 5


@pytest.mark.parametrize("scale", [1, 2, 3, 4])
def test_integer_font_scaling_uses_solid_pixel_blocks(scale):
    fb = FrameBuffer()
    fb.displayText(0, 0, b"A", font_id=0, scale=scale)

    for y in range(0, 8 * scale, scale):
        for x in range(0, 5 * scale, scale):
            block = [
                fb.pixels[y + dy][x + dx]
                for dy in range(scale)
                for dx in range(scale)
            ]
            assert len(set(block)) == 1


def test_unknown_stored_byte_renders_as_question_mark():
    unknown = FrameBuffer()
    question = FrameBuffer()

    unknown.displayText(0, 0, bytes([0xFF]), font_id=0)
    question.displayText(0, 0, b"?", font_id=0)

    assert pixels(unknown) == pixels(question)


def test_text_is_clipped_at_all_framebuffer_edges():
    fb = FrameBuffer()

    fb.displayText(-4, -4, b"A", font_id=0, scale=2)
    fb.displayText(124, 60, b"A", font_id=0, scale=2)

    assert any(any(row) for row in fb.pixels)


def test_newline_uses_scaled_line_spacing():
    font = get_font(0)
    fb = FrameBuffer()

    fb.displayText(0, 0, b"A\nA", font_id=0, scale=2)

    second_line_y = (font.height + font.line_spacing) * 2
    assert any(fb.pixels[y][x] for y in range(second_line_y, 64) for x in range(10))


def test_invalid_font_and_scale_fail_cleanly():
    fb = FrameBuffer()

    with pytest.raises(ValueError, match="Invalid font id"):
        fb.displayText(0, 0, b"A", font_id=5)

    with pytest.raises(ValueError, match="Invalid font scale"):
        fb.displayText(0, 0, b"A", scale=0)
