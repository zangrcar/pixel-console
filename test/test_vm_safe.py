import pytest

from src.assembler import assemble_text
from src.sprite import BUILTIN_SPRITES
from src.vm import (
    OP_CLEAR,
    OP_END,
    OP_FONT,
    OP_JMP,
    OP_SETV,
    OP_SHOW,
    OP_SPR,
    OP_TEXT,
    PixelVM,
    VMError,
)


def test_vm_resets_all_program_state_between_runs():
    frames = []
    pixel_vm = PixelVM(
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks))
    )
    first = assemble_text(
        "clear 1\nmode 2\nsetv 0 99\norigin 10 11\nfont 4 3\nframe 1\nend"
    )
    second = assemble_text("pset 0 0\nend")

    pixel_vm.run(first)
    assert pixel_vm.frame_number == 1

    pixel_vm.run(second)

    assert pixel_vm.pc == len(second)
    assert pixel_vm.vars == [0] * 8
    assert (pixel_vm.ox, pixel_vm.oy) == (0, 0)
    assert pixel_vm.mode == 1
    assert pixel_vm.font_id == 0
    assert pixel_vm.font_scale == 1
    assert pixel_vm.frame_number == 0
    assert pixel_vm.fb.pixels[0][0] == 1
    assert sum(sum(row) for row in pixel_vm.fb.pixels) == 1


def test_execution_limit_raises_vm_error():
    code = assemble_text("loop:\nnop\njmp loop")

    with pytest.raises(VMError, match="Execution limit exceeded"):
        PixelVM().run(code, max_steps=5)


@pytest.mark.parametrize(
    "code, message",
    [
        (bytes([0xFF]), "Unknown opcode"),
        (bytes([OP_CLEAR]), "Unexpected end of bytecode"),
        (bytes([OP_SETV, 8, 1, OP_END]), "Invalid variable index"),
        (bytes([OP_JMP, 0xFC, 0xFF, OP_END]), "invalid address -1"),
        (
            bytes([OP_SPR, 0, 0, 0, BUILTIN_SPRITES[0].frame_count, OP_END]),
            "Invalid frame",
        ),
        (bytes([OP_FONT, 5, 1, OP_END]), "Invalid font id"),
        (bytes([OP_FONT, 0, 5, OP_END]), "Invalid font scale"),
        (bytes([OP_TEXT, 0, 0, 1, 0xFF, OP_END]), "unsupported byte"),
        (bytes([0x01]), "fall past end"),
    ],
)
def test_invalid_bytecode_becomes_controlled_vm_error(code, message):
    with pytest.raises(VMError, match=message):
        PixelVM().run(code)


def test_invalid_program_is_rejected_before_first_frame():
    frames = []
    code = bytes([OP_SHOW, 0xFF])
    pixel_vm = PixelVM(
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks))
    )

    with pytest.raises(VMError, match="Unknown opcode"):
        pixel_vm.run(code)

    assert frames == []
    assert pixel_vm.frame_number == 0


def test_invalid_bytecode_input_type_becomes_vm_error():
    with pytest.raises(VMError, match="Invalid bytecode data"):
        PixelVM().run([300])


def test_max_frames_stops_infinite_animation_cleanly():
    frames = []
    code = assemble_text("loop:\nframe 2\njmp loop")
    pixel_vm = PixelVM(
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks))
    )

    pixel_vm.run(code, max_frames=3, max_steps=100)

    assert len(frames) == 3
    assert [ticks for _framebuffer, ticks in frames] == [2, 2, 2]
    assert pixel_vm.frame_number == 3
