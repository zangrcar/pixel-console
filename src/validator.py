from __future__ import annotations

from dataclasses import dataclass

from src.font import FONTS, is_text_byte_supported
from src.sprite import BUILTIN_SPRITES
from src.vm import (
    OP_END,
    OP_NOP,
    OP_CLEAR,
    OP_MODE,
    OP_SHOW,
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
)


class ValidationError(Exception):
    pass


@dataclass
class InstructionInfo:
    start: int
    end: int
    opcode: int
    jump_target: int | None = None


def _read_u8(code: bytes, pc: int) -> tuple[int, int]:
    if pc >= len(code):
        raise ValidationError("Unexpected end of bytecode")
    return code[pc], pc + 1


def _read_i16(code: bytes, pc: int) -> tuple[int, int]:
    if pc + 2 > len(code):
        raise ValidationError("Unexpected end of bytecode")
    raw = code[pc] | (code[pc + 1] << 8)
    if raw >= 0x8000:
        raw -= 0x10000
    return raw, pc + 2


def _check_var(value: int) -> None:
    if not 0 <= value <= 7:
        raise ValidationError(f"Invalid variable index: {value}")


def _check_varpair(value: int) -> None:
    x_var = value >> 4
    y_var = value & 0x0F

    if not 0 <= x_var <= 7:
        raise ValidationError(f"Invalid x variable in varpair: {x_var}")

    if not 0 <= y_var <= 7:
        raise ValidationError(f"Invalid y variable in varpair: {y_var}")


def _check_sprite(sprite_id: int, frame: int, card_sprites) -> None:
    if sprite_id < 128:
        if sprite_id >= len(BUILTIN_SPRITES):
            raise ValidationError(f"Invalid built-in sprite id: {sprite_id}")

        sprite = BUILTIN_SPRITES[sprite_id]

        if frame >= sprite.frame_count:
            raise ValidationError(
                f"Invalid frame {frame} for built-in sprite {sprite_id}"
            )

        return

    card_index = sprite_id - 128

    if card_index >= len(card_sprites):
        raise ValidationError(f"Invalid card sprite id: {sprite_id}")

    sprite = card_sprites[card_index]

    if frame >= sprite.frame_count:
        raise ValidationError(
            f"Invalid frame {frame} for card sprite {sprite_id}"
        )


def validate_program(code: bytes, card_sprites=None) -> None:
    if card_sprites is None:
        card_sprites = []

    if not code:
        raise ValidationError("Empty program")

    instructions: list[InstructionInfo] = []
    pc = 0

    while pc < len(code):
        start = pc
        opcode, pc = _read_u8(code, pc)
        jump_target = None

        if opcode in (OP_END, OP_NOP, OP_SHOW):
            pass

        elif opcode == OP_CLEAR:
            color, pc = _read_u8(code, pc)

            if color not in (0, 1):
                raise ValidationError(f"Invalid clear color: {color}")

        elif opcode == OP_MODE:
            mode, pc = _read_u8(code, pc)

            if not 0 <= mode <= 3:
                raise ValidationError(f"Invalid draw mode: {mode}")

        elif opcode in (OP_WAIT, OP_FRAME):
            _arg, pc = _read_u8(code, pc)

        elif opcode == OP_FONT:
            font_id, pc = _read_u8(code, pc)
            scale, pc = _read_u8(code, pc)

            if font_id not in FONTS:
                raise ValidationError(f"Invalid font id: {font_id}")

            if not 1 <= scale <= 4:
                raise ValidationError(f"Invalid font scale: {scale}")

        elif opcode == OP_JMP:
            offset, pc = _read_i16(code, pc)
            jump_target = pc + offset

        elif opcode in (OP_SETV, OP_ADDV, OP_RANDV):
            var, pc = _read_u8(code, pc)
            _check_var(var)
            _arg, pc = _read_u8(code, pc)

        elif opcode == OP_JNZ:
            var, pc = _read_u8(code, pc)
            _check_var(var)
            offset, pc = _read_i16(code, pc)
            jump_target = pc + offset

        elif opcode == OP_JLT:
            var, pc = _read_u8(code, pc)
            _check_var(var)
            _value, pc = _read_u8(code, pc)
            offset, pc = _read_i16(code, pc)
            jump_target = pc + offset

        elif opcode == OP_DJNZ:
            var, pc = _read_u8(code, pc)
            _check_var(var)
            offset, pc = _read_i16(code, pc)
            jump_target = pc + offset

        elif opcode == OP_ORIGIN:
            _x, pc = _read_u8(code, pc)
            _y, pc = _read_u8(code, pc)

        elif opcode == OP_ORIGINV:
            packed, pc = _read_u8(code, pc)
            _check_varpair(packed)

        elif opcode == OP_PSET:
            _x, pc = _read_u8(code, pc)
            _y, pc = _read_u8(code, pc)

        elif opcode in (OP_LINE, OP_RECT, OP_FRECT, OP_INVRECT):
            for _ in range(4):
                _arg, pc = _read_u8(code, pc)

        elif opcode == OP_TEXT:
            _x, pc = _read_u8(code, pc)
            _y, pc = _read_u8(code, pc)
            length, pc = _read_u8(code, pc)

            if length > 64:
                raise ValidationError("Text too long")

            if pc + length > len(code):
                raise ValidationError("Truncated text instruction")

            text_data = code[pc:pc + length]

            if not all(is_text_byte_supported(byte) for byte in text_data):
                raise ValidationError("Text contains an unsupported byte")

            pc += length

        elif opcode == OP_SPR:
            _x, pc = _read_u8(code, pc)
            _y, pc = _read_u8(code, pc)
            sprite_id, pc = _read_u8(code, pc)
            frame, pc = _read_u8(code, pc)
            _check_sprite(sprite_id, frame, card_sprites)

        elif opcode == OP_SPRV:
            packed, pc = _read_u8(code, pc)
            _check_varpair(packed)
            sprite_id, pc = _read_u8(code, pc)
            frame, pc = _read_u8(code, pc)
            _check_sprite(sprite_id, frame, card_sprites)

        elif opcode == OP_MOVE:
            _dx, pc = _read_u8(code, pc)
            _dy, pc = _read_u8(code, pc)

        else:
            raise ValidationError(f"Unknown opcode: 0x{opcode:02X}")

        instructions.append(
            InstructionInfo(
                start=start,
                end=pc,
                opcode=opcode,
                jump_target=jump_target,
            )
        )

    starts = {instruction.start for instruction in instructions}

    for instruction in instructions:
        if instruction.jump_target is None:
            continue

        if instruction.jump_target not in starts:
            raise ValidationError(
                f"Jump from {instruction.start} targets invalid address {instruction.jump_target}"
            )

    if instructions[-1].opcode not in (OP_END, OP_JMP):
        raise ValidationError(
            f"Program can fall past end of code after byte {instructions[-1].start}"
        )
