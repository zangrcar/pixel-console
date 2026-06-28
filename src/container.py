from src.sprite import Sprite

MAGIC = b"PXL1"


def pack_sprite_bank(sprites):
    
    if len(sprites) > 255:
        raise ValueError("Too many sprites, max 255")

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


def unpack_sprite_bank(data):
    if not data:
        return []

    sprites = []
    pc = 0

    sprite_count = data[pc]
    pc += 1

    for _ in range(sprite_count):
        width = data[pc]
        height = data[pc + 1]
        frame_count = data[pc + 2]
        encoding = data[pc + 3]
        data_len = int.from_bytes(data[pc + 4:pc + 6], "little")
        pc += 6

        if encoding != 0:
            raise ValueError("Only raw sprites supported for now")

        raw = data[pc:pc + data_len]
        pc += data_len

        bytes_per_row = (width + 7) // 8
        bytes_per_frame = bytes_per_row * height
        expected_len = bytes_per_frame * frame_count

        if data_len != expected_len:
            raise ValueError("Bad sprite data length")

        frames = []

        for i in range(frame_count):
            start = i * bytes_per_frame
            end = start + bytes_per_frame
            frames.append(raw[start:end])

        sprites.append(Sprite(width, height, frame_count, frames))

    return sprites


def wrap_program(code, sprites=None):
    if sprites is None:
        sprites = []

    sprite_bank = pack_sprite_bank(sprites)

    total_len = 4 + 2 + 2 + len(sprite_bank) + len(code)

    if total_len > 888:
        raise ValueError("Program is too large for NTAG216")

    return (
        MAGIC +
        total_len.to_bytes(2, "little") +
        len(sprite_bank).to_bytes(2, "little") +
        sprite_bank +
        code
    )


def unwrap_program(data):
    if data[:4] != MAGIC:
        raise ValueError("Bad magic")

    total_len = int.from_bytes(data[4:6], "little")
    sprite_bank_len = int.from_bytes(data[6:8], "little")

    if total_len > len(data):
        raise ValueError("Truncated container")

    if 8 + sprite_bank_len > total_len:
        raise ValueError("Bad sprite bank length")

    sprite_start = 8
    sprite_end = sprite_start + sprite_bank_len
    code_start = sprite_end

    sprite_bank_data = data[sprite_start:sprite_end]
    code = data[code_start:total_len]

    sprites = unpack_sprite_bank(sprite_bank_data)

    return code, sprites

# backward compatibility. Later remove

def wrap_code(code):
    return wrap_program(code, sprites=[])


def unwrap_code(data):
    code, sprites = unwrap_program(data)
    return code