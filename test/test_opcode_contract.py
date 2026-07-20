import pytest

from src import vm
from src.assembler import OPCODES, assemble_text
from src.container import unwrap_program, wrap_program
from src.validator import validate_program
from src.vm import PixelVM


OPCODE_CASES = [
    ("end", 0x00, "end", 1),
    ("nop", 0x01, "nop", 1),
    ("clear", 0x02, "clear 0", 2),
    ("mode", 0x03, "mode 1", 2),
    ("show", 0x04, "show", 1),
    ("wait", 0x05, "wait 1", 2),
    ("frame", 0x06, "frame 1", 2),
    ("jmp", 0x07, "jmp target\ntarget:", 3),
    ("setv", 0x08, "setv 0 1", 3),
    ("addv", 0x09, "addv 0 -1", 3),
    ("randv", 0x0A, "randv 0 1", 3),
    ("jnz", 0x0B, "jnz 0 target\ntarget:", 4),
    ("jlt", 0x0C, "jlt 0 1 target\ntarget:", 5),
    ("djnz", 0x0D, "djnz 0 target\ntarget:", 4),
    ("origin", 0x0E, "origin 1 2", 3),
    ("originv", 0x0F, "originv V0,V1", 2),
    ("pset", 0x10, "pset 1 2", 3),
    ("line", 0x11, "line 1 2 3 4", 5),
    ("rect", 0x12, "rect 1 2 3 4", 5),
    ("frect", 0x13, "frect 1 2 3 4", 5),
    ("invrect", 0x14, "invrect 1 2 3 4", 5),
    ("text", 0x15, 'text 1 2 "A"', 5),
    ("font", 0x16, "font 0 1", 3),
    ("spr", 0x17, "spr 1 2 0 0", 5),
    ("sprv", 0x18, "sprv V0,V1 0 0", 4),
    ("move", 0x19, "move -1 2", 3),
]


@pytest.mark.parametrize("name, opcode, source, size", OPCODE_CASES)
def test_opcode_value_and_instruction_size(name, opcode, source, size):
    assert OPCODES[name] == opcode
    assert getattr(vm, f"OP_{name.upper()}") == opcode

    code = assemble_text(source)

    assert code[0] == opcode
    assert len(code) == size


def test_moveorig_remains_an_undocumented_move_alias():
    assert OPCODES["moveorig"] == OPCODES["move"] == 0x19
    assert assemble_text("moveorig -2 3") == assemble_text("move -2 3")


def test_forward_jump_is_relative_to_end_of_instruction():
    code = assemble_text("jmp target\nnop\ntarget:\nend")

    assert code == bytes([0x07, 0x01, 0x00, 0x01, 0x00])
    validate_program(code)


def test_backward_jump_is_relative_to_end_of_instruction():
    code = assemble_text("start:\nnop\njmp start")

    assert code == bytes([0x01, 0x07, 0xFC, 0xFF])
    validate_program(code)


def test_font_argument_is_consumed_by_vm():
    code = assemble_text("font 1 2\npset 1 2\nend")
    pixel_vm = PixelVM()

    pixel_vm.run(code)

    assert pixel_vm.fb.pixels[2][1] == 1
    assert pixel_vm.font_id == 1
    assert pixel_vm.font_scale == 2


def test_assemble_wrap_unwrap_validate_and_run():
    source = "clear 0\nmode 1\nrect 0 0 8 8\nframe 2\nend"
    frames = []

    code = assemble_text(source)
    program = wrap_program(code)
    loaded_code, loaded_sprites = unwrap_program(program)
    validate_program(loaded_code, loaded_sprites)

    pixel_vm = PixelVM(
        card_sprites=loaded_sprites,
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks)),
    )
    pixel_vm.run(loaded_code)

    assert loaded_code == code
    assert len(frames) == 1
    assert frames[0][1] == 2
    assert frames[0][0].pixels[0][0] == 1
