import pytest

from src.assembler import assemble_file, assemble_text
from src.font import encode_text
from src.framebuffer import FrameBuffer
from src.validator import ValidationError, validate_program
from src.vm import OP_END, OP_FONT, PixelVM, VMError


TEXT_CASES = [
    ("ŠČŽ", bytes([0x81, 0x80, 0x82])),
    ("ščž", bytes([0x84, 0x83, 0x85])),
    ("Živjo", bytes([0x82]) + b"ivjo"),
    ("Čestitke!", bytes([0x80]) + b"estitke!"),
    ("Srečen rojstni dan!", b"Sre" + bytes([0x83]) + b"en rojstni dan!"),
]


@pytest.mark.parametrize("text, expected", TEXT_CASES)
def test_slovenian_text_uses_one_byte_per_character(text, expected):
    code = assemble_text(f'text 0 0 "{text}"')

    assert encode_text(text) == expected
    assert code[:4] == bytes([0x15, 0, 0, len(expected)])
    assert code[4:] == expected
    assert len(expected) == len(text)


def test_assemble_file_reads_utf8_source(tmp_path):
    source = tmp_path / "slovenian.pxla"
    output = tmp_path / "slovenian.bin"
    source.write_text('text 0 0 "ČŠŽ čšž"\nend\n', encoding="utf-8")

    assemble_file(source, output)

    assert bytes([0x80, 0x81, 0x82, 0x20, 0x83, 0x84, 0x85]) in output.read_bytes()


def test_unsupported_unicode_reports_line_and_character():
    with pytest.raises(ValueError, match="Line 2.*€.*only ASCII"):
        assemble_text('clear 0\ntext 0 0 "Cena 10 €"\nend')


@pytest.mark.parametrize("font_id", range(5))
@pytest.mark.parametrize("scale", range(1, 5))
def test_vm_uses_selected_font_and_scale(font_id, scale):
    frames = []
    code = assemble_text(
        f'font {font_id} {scale}\ntext 0 0 "Ča"\nshow\nend'
    )
    validate_program(code)

    pixel_vm = PixelVM(
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks))
    )
    pixel_vm.run(code)

    assert pixel_vm.font_id == font_id
    assert pixel_vm.font_scale == scale
    assert len(frames) == 1
    assert any(any(row) for row in frames[0][0].pixels)


def test_vm_defaults_to_classic_scale_one():
    pixel_vm = PixelVM()

    assert pixel_vm.font_id == 0
    assert pixel_vm.font_scale == 1


@pytest.mark.parametrize(
    "code, message",
    [
        (bytes([OP_FONT, 5, 1, OP_END]), "Invalid font id"),
        (bytes([OP_FONT, 0, 0, OP_END]), "Invalid font scale"),
        (bytes([OP_FONT, 0, 5, OP_END]), "Invalid font scale"),
    ],
)
def test_validator_rejects_invalid_font_state(code, message):
    with pytest.raises(ValidationError, match=message):
        validate_program(code)


@pytest.mark.parametrize(
    "code, message",
    [
        (bytes([OP_FONT, 5, 1, OP_END]), "Invalid font id"),
        (bytes([OP_FONT, 0, 5, OP_END]), "Invalid font scale"),
    ],
)
def test_vm_rejects_invalid_font_state(code, message):
    with pytest.raises(VMError, match=message):
        PixelVM().run(code)


def test_validator_accepts_internal_slovenian_bytes():
    code = assemble_text('text 0 0 "ČŠŽ čšž"\nend')

    validate_program(code)


def test_vm_renders_complete_slovenian_text_line():
    code = assemble_text('font 0 1\ntext 0 0 "Srečen rojstni dan!"\nend')
    pixel_vm = PixelVM()

    pixel_vm.run(code)

    assert any(
        pixel_vm.fb.pixels[y][x]
        for y in range(8)
        for x in range(100, 128)
    )


@pytest.mark.parametrize("byte", range(0x80, 0x86))
def test_slovenian_glyphs_do_not_render_as_fallback(byte):
    special = FrameBuffer()
    fallback = FrameBuffer()

    special.displayText(0, 0, bytes([byte]))
    fallback.displayText(0, 0, b"?")

    assert special.pixels != fallback.pixels


def test_validator_rejects_unsupported_text_byte():
    code = bytes([0x15, 0, 0, 1, 0xFF, OP_END])

    with pytest.raises(ValidationError, match="unsupported byte"):
        validate_program(code)
