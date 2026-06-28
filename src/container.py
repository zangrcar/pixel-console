from __future__ import annotations

from src.sprite import Sprite

MAGIC = b"PXL1"
HEADER_SIZE = 10
MAX_NTAG216_BYTES = 888


class ContainerError(Exception):
    pass


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF

    for byte in data:
        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return crc


def pack_sprite_bank(sprites):
    if sprites is None:
        sprites = []

    if len(sprites) > 127:
        raise ValueError("Too many card sprites, max 127")

    out = bytearray()
    out.append(len(sprites))

    for sprite in sprites:
        out.append(sprite.width)
        out.append(sprite.height)
        out.append(sprite.frame_count)
        out.append(0)  # encoding: 0 = raw

        frame_data = b"".join(sprite.frames)

        out.extend(len(frame_data).to_bytes(2, "little"))
        out.extend(frame_data)

    return bytes(out)


def unpack_sprite_bank(data: bytes):
    if not data:
        return []

    sprites = []
    pc = 0

    sprite_count = data[pc]
    pc += 1

    for _ in range(sprite_count):
        if pc + 6 > len(data):
            raise ContainerError("Truncated sprite header")

        width = data[pc]
        height = data[pc + 1]
        frame_count = data[pc + 2]
        encoding = data[pc + 3]
        data_len = int.from_bytes(data[pc + 4:pc + 6], "little")
        pc += 6

        if width == 0 or height == 0 or frame_count == 0:
            raise ContainerError("Invalid sprite dimensions or frame count")

        if encoding != 0:
            raise ContainerError("Only raw sprite encoding is supported")

        if pc + data_len > len(data):
            raise ContainerError("Truncated sprite data")

        raw = data[pc:pc + data_len]
        pc += data_len

        bytes_per_row = (width + 7) // 8
        bytes_per_frame = bytes_per_row * height
        expected_len = bytes_per_frame * frame_count

        if data_len != expected_len:
            raise ContainerError("Bad sprite data length")

        frames = []

        for frame_index in range(frame_count):
            start = frame_index * bytes_per_frame
            end = start + bytes_per_frame
            frames.append(raw[start:end])

        sprites.append(Sprite(width, height, frame_count, frames))

    if pc != len(data):
        raise ContainerError("Extra bytes after sprite bank")

    return sprites


def wrap_program(code: bytes, sprites=None) -> bytes:
    if sprites is None:
        sprites = []

    sprite_bank = pack_sprite_bank(sprites)

    total_len = HEADER_SIZE + len(sprite_bank) + len(code)

    if total_len > MAX_NTAG216_BYTES:
        raise ValueError("Program is too large for NTAG216")

    out = bytearray()
    out.extend(MAGIC)
    out.extend(total_len.to_bytes(2, "little"))
    out.extend(len(sprite_bank).to_bytes(2, "little"))
    out.extend((0).to_bytes(2, "little"))  # CRC placeholder
    out.extend(sprite_bank)
    out.extend(code)

    crc_data = bytearray(out)
    crc_data[8] = 0
    crc_data[9] = 0

    crc = crc16_ccitt(bytes(crc_data))
    out[8:10] = crc.to_bytes(2, "little")

    return bytes(out)


def unwrap_program(data: bytes):
    if len(data) < HEADER_SIZE:
        raise ContainerError("Container too short")

    if data[:4] != MAGIC:
        raise ContainerError("Bad magic")

    total_len = int.from_bytes(data[4:6], "little")
    sprite_bank_len = int.from_bytes(data[6:8], "little")
    stored_crc = int.from_bytes(data[8:10], "little")

    if total_len < HEADER_SIZE:
        raise ContainerError("Bad total length")

    if total_len > MAX_NTAG216_BYTES:
        raise ContainerError("Container too large")

    if total_len > len(data):
        raise ContainerError("Truncated container")

    used = data[:total_len]

    crc_data = bytearray(used)
    crc_data[8] = 0
    crc_data[9] = 0

    actual_crc = crc16_ccitt(bytes(crc_data))

    if actual_crc != stored_crc:
        raise ContainerError("Bad CRC")

    sprite_start = HEADER_SIZE
    sprite_end = sprite_start + sprite_bank_len

    if sprite_end > total_len:
        raise ContainerError("Bad sprite bank length")

    sprite_bank_data = used[sprite_start:sprite_end]
    code = used[sprite_end:total_len]

    sprites = unpack_sprite_bank(sprite_bank_data)

    if not code:
        raise ContainerError("Empty code section")

    return code, sprites


# Backward compatibility helpers.
# Keep these only while old code still imports wrap_code / unwrap_code.

def wrap_code(code: bytes) -> bytes:
    return wrap_program(code, sprites=[])


def unwrap_code(data: bytes) -> bytes:
    code, _sprites = unwrap_program(data)
    return code