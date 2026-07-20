import pytest

from src.assembler import assemble_text
from src.sprite import BUILTIN_SPRITES, Sprite
from src.validator import ValidationError, validate_program
from src.vm import (
    OP_ADDV,
    OP_CLEAR,
    OP_DJNZ,
    OP_FONT,
    OP_FRAME,
    OP_FRECT,
    OP_INVRECT,
    OP_JLT,
    OP_JMP,
    OP_JNZ,
    OP_LINE,
    OP_MODE,
    OP_MOVE,
    OP_ORIGIN,
    OP_ORIGINV,
    OP_PSET,
    OP_RANDV,
    OP_RECT,
    OP_SETV,
    OP_SPR,
    OP_SPRV,
    OP_TEXT,
    OP_WAIT,
)


ARGUMENT_OPCODES = [
    OP_CLEAR,
    OP_MODE,
    OP_WAIT,
    OP_FRAME,
    OP_JMP,
    OP_SETV,
    OP_ADDV,
    OP_RANDV,
    OP_JNZ,
    OP_JLT,
    OP_DJNZ,
    OP_ORIGIN,
    OP_ORIGINV,
    OP_PSET,
    OP_LINE,
    OP_RECT,
    OP_FRECT,
    OP_INVRECT,
    OP_TEXT,
    OP_FONT,
    OP_SPR,
    OP_SPRV,
    OP_MOVE,
]


@pytest.mark.parametrize("opcode", ARGUMENT_OPCODES)
def test_every_argument_opcode_rejects_missing_arguments(opcode):
    with pytest.raises(ValidationError, match="Unexpected end of bytecode"):
        validate_program(bytes([opcode]))


def test_unknown_opcode_is_rejected():
    with pytest.raises(ValidationError, match="Unknown opcode: 0xFF"):
        validate_program(bytes([0xFF]))


@pytest.mark.parametrize(
    "code, message",
    [
        (bytes([OP_CLEAR, 2, 0x00]), "Invalid clear color"),
        (bytes([OP_MODE, 4, 0x00]), "Invalid draw mode"),
        (bytes([OP_SETV, 8, 1, 0x00]), "Invalid variable index"),
        (bytes([OP_ORIGINV, 0x80, 0x00]), "Invalid x variable"),
        (bytes([OP_ORIGINV, 0x08, 0x00]), "Invalid y variable"),
        (bytes([OP_FONT, 5, 1, 0x00]), "Invalid font id"),
        (bytes([OP_FONT, 0, 0, 0x00]), "Invalid font scale"),
    ],
)
def test_invalid_instruction_arguments_are_rejected(code, message):
    with pytest.raises(ValidationError, match=message):
        validate_program(code)


def test_invalid_builtin_sprite_frame_is_rejected():
    frame = BUILTIN_SPRITES[0].frame_count
    code = bytes([OP_SPR, 0, 0, 0, frame, 0x00])

    with pytest.raises(ValidationError, match="Invalid frame.*built-in sprite 0"):
        validate_program(code)


def test_valid_builtin_sprite_frame_is_accepted():
    frame = BUILTIN_SPRITES[127].frame_count - 1
    code = bytes([OP_SPR, 0, 0, 127, frame, 0x00])

    validate_program(code)


def test_invalid_card_sprite_id_and_frame_are_rejected():
    card_sprite = Sprite(8, 8, 1, [bytes(8)])

    with pytest.raises(ValidationError, match="Invalid card sprite id: 129"):
        validate_program(bytes([OP_SPR, 0, 0, 129, 0, 0x00]), [card_sprite])

    with pytest.raises(ValidationError, match="Invalid frame 1 for card sprite 128"):
        validate_program(bytes([OP_SPR, 0, 0, 128, 1, 0x00]), [card_sprite])


@pytest.mark.parametrize(
    "code, message",
    [
        (bytes([OP_TEXT, 0, 0, 65]) + bytes(65) + bytes([0x00]), "Text too long"),
        (bytes([OP_TEXT, 0, 0, 2, ord("A")]), "Truncated text"),
        (bytes([OP_TEXT, 0, 0, 1, 0xFF, 0x00]), "unsupported byte"),
    ],
)
def test_invalid_text_payload_is_rejected(code, message):
    with pytest.raises(ValidationError, match=message):
        validate_program(code)


@pytest.mark.parametrize(
    "source, address",
    [
        ("jmp middle\ntext 0 0 \"A\"\nmiddle:\nend", None),
        (None, -1),
        (None, 4),
    ],
)
def test_jump_target_must_be_valid_instruction_start(source, address):
    if source is not None:
        code = bytearray(assemble_text(source))
        code[1:3] = (2).to_bytes(2, "little", signed=True)
        invalid_code = bytes(code)
    else:
        offset = address - 3
        invalid_code = bytes([OP_JMP]) + offset.to_bytes(2, "little", signed=True) + bytes([0x00])

    with pytest.raises(ValidationError, match="targets invalid address"):
        validate_program(invalid_code)


def test_valid_forward_and_backward_jumps_are_accepted():
    validate_program(assemble_text("jmp done\nnop\ndone:\nend"))
    validate_program(assemble_text("loop:\nnop\njmp loop"))


def test_program_that_can_fall_past_end_is_rejected():
    with pytest.raises(ValidationError, match="fall past end"):
        validate_program(bytes([0x01]))


def test_infinite_program_ending_in_jump_is_accepted():
    validate_program(assemble_text("loop:\nnop\njmp loop"))
