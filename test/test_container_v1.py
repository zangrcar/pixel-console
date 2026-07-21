import pytest

from src.container import (
    CRC_OFFSET,
    FORMAT_VERSION,
    HEADER_SIZE,
    MAGIC,
    MAX_NTAG216_BYTES,
    SPRITE_BANK_LENGTH_OFFSET,
    TOTAL_LENGTH_OFFSET,
    CRCError,
    ContainerError,
    UnsupportedVersionError,
    crc16_ccitt,
    pack_sprite_bank,
    unpack_sprite_bank,
    unwrap_program,
    wrap_program,
)
from src.sprite import Sprite


def make_container(sprite_bank=b"\x00", code=b"\x00", version=FORMAT_VERSION):
    total_len = HEADER_SIZE + len(sprite_bank) + len(code)
    data = bytearray(MAGIC)
    data.append(version)
    data.extend(total_len.to_bytes(2, "little"))
    data.extend(len(sprite_bank).to_bytes(2, "little"))
    data.extend(b"\x00\x00")
    data.extend(sprite_bank)
    data.extend(code)
    crc = crc16_ccitt(bytes(data))
    data[CRC_OFFSET:CRC_OFFSET + 2] = crc.to_bytes(2, "little")
    return bytes(data)


def one_pixel_sprite(value=0x80):
    return Sprite(1, 1, 1, [bytes([value])])


def test_v1_header_layout_and_crc():
    code = bytes([0x01, 0x00])
    program = wrap_program(code)

    assert program[:4] == MAGIC
    assert program[4] == FORMAT_VERSION == 1
    assert int.from_bytes(program[5:7], "little") == len(program)
    assert int.from_bytes(program[7:9], "little") == 1
    assert len(program) == HEADER_SIZE + 1 + len(code)

    crc_data = bytearray(program)
    stored_crc = int.from_bytes(crc_data[CRC_OFFSET:CRC_OFFSET + 2], "little")
    crc_data[CRC_OFFSET:CRC_OFFSET + 2] = b"\x00\x00"
    assert stored_crc == crc16_ccitt(bytes(crc_data))


def test_v1_round_trip_with_card_sprite_and_nfc_padding():
    code = bytes([0x00])
    program = wrap_program(code, [one_pixel_sprite()])
    padded = program + bytes(MAX_NTAG216_BYTES - len(program))

    loaded_code, sprites = unwrap_program(padded)

    assert loaded_code == code
    assert len(sprites) == 1
    assert (sprites[0].width, sprites[0].height, sprites[0].frame_count) == (1, 1, 1)
    assert sprites[0].frames == [b"\x80"]


def test_old_unversioned_header_is_rejected():
    old = b"PXL1" + bytes([12, 0, 1, 0, 0, 0, 0, 0])

    with pytest.raises(UnsupportedVersionError):
        unwrap_program(old)


@pytest.mark.parametrize("version", [0, 2, 255])
def test_unsupported_version_is_rejected(version):
    with pytest.raises(UnsupportedVersionError, match=f"version: {version}"):
        unwrap_program(make_container(version=version))


def test_bad_magic_and_crc_are_rejected():
    bad_magic = bytearray(make_container())
    bad_magic[0] = ord("X")

    with pytest.raises(ContainerError, match="Bad magic"):
        unwrap_program(bytes(bad_magic))

    bad_crc = bytearray(make_container())
    bad_crc[-1] ^= 0xFF

    with pytest.raises(CRCError, match="Bad CRC"):
        unwrap_program(bytes(bad_crc))


def test_truncated_input_is_rejected_and_extra_card_capacity_is_ignored():
    program = make_container()

    with pytest.raises(ContainerError, match="Container too short"):
        unwrap_program(program[:HEADER_SIZE - 1])

    with pytest.raises(ContainerError, match="Truncated container"):
        unwrap_program(program[:-1])

    padded_for_larger_card = program + bytes(MAX_NTAG216_BYTES + 100)
    code, sprites = unwrap_program(padded_for_larger_card)

    assert code == b"\x00"
    assert sprites == []


def test_bad_total_and_sprite_bank_lengths_are_rejected():
    bad_total = bytearray(make_container())
    bad_total[TOTAL_LENGTH_OFFSET:TOTAL_LENGTH_OFFSET + 2] = (HEADER_SIZE).to_bytes(2, "little")

    with pytest.raises(ContainerError, match="Bad total length"):
        unwrap_program(bytes(bad_total))

    bad_bank = bytearray(make_container())
    bad_bank[SPRITE_BANK_LENGTH_OFFSET:SPRITE_BANK_LENGTH_OFFSET + 2] = (99).to_bytes(2, "little")
    bad_bank[CRC_OFFSET:CRC_OFFSET + 2] = b"\x00\x00"
    bad_bank[CRC_OFFSET:CRC_OFFSET + 2] = crc16_ccitt(bytes(bad_bank)).to_bytes(2, "little")

    with pytest.raises(ContainerError, match="Bad sprite bank length"):
        unwrap_program(bytes(bad_bank))


def test_exact_ntag216_limit_is_allowed_and_one_more_is_rejected():
    code_at_limit = bytes(MAX_NTAG216_BYTES - HEADER_SIZE - 1)

    assert len(wrap_program(code_at_limit)) == MAX_NTAG216_BYTES

    with pytest.raises(ValueError, match="too large for NTAG216"):
        wrap_program(code_at_limit + b"\x00")

    larger_card_program = wrap_program(code_at_limit + b"\x00", max_size=None)

    assert len(larger_card_program) == MAX_NTAG216_BYTES + 1
    assert unwrap_program(larger_card_program)[0] == code_at_limit + b"\x00"


def test_author_can_select_a_different_card_capacity():
    code = bytes(900)

    assert len(wrap_program(code, max_size=1024)) <= 1024

    with pytest.raises(ValueError, match="configured card capacity: 900 bytes"):
        wrap_program(code, max_size=900)


def test_sprite_bank_supports_count_for_ids_128_through_255():
    packed = pack_sprite_bank([one_pixel_sprite()] * 128)

    assert packed[0] == 128
    assert len(unpack_sprite_bank(packed)) == 128

    with pytest.raises(ValueError, match="max 128"):
        pack_sprite_bank([one_pixel_sprite()] * 129)


@pytest.mark.parametrize(
    "sprite, message",
    [
        (Sprite(0, 1, 1, [b""]), "Invalid dimensions"),
        (Sprite(1, 1, 0, []), "Invalid frame count"),
        (Sprite(1, 1, 2, [b"\x80"]), "Frame count mismatch"),
        (Sprite(8, 8, 1, [b"\x00"]), "Bad frame data length"),
    ],
)
def test_invalid_sprite_objects_cannot_be_packed(sprite, message):
    with pytest.raises(ValueError, match=message):
        pack_sprite_bank([sprite])


@pytest.mark.parametrize(
    "sprite_bank, message",
    [
        (b"", "Missing sprite bank"),
        (b"\x01", "Truncated sprite header"),
        (bytes([1, 0, 1, 1, 0, 0, 0]), "Invalid sprite dimensions"),
        (bytes([1, 1, 1, 1, 1, 1, 0, 0]), "Only raw sprite encoding"),
        (bytes([1, 8, 8, 1, 0, 8, 0]) + bytes(7), "Truncated sprite data"),
        (bytes([1, 8, 8, 1, 0, 7, 0]) + bytes(7), "Bad sprite data length"),
        (b"\x00\x00", "Extra bytes after sprite bank"),
    ],
)
def test_malformed_sprite_bank_is_rejected(sprite_bank, message):
    with pytest.raises(ContainerError, match=message):
        unpack_sprite_bank(sprite_bank)


def test_empty_code_is_rejected_on_wrap_and_unwrap():
    with pytest.raises(ValueError, match="Code section cannot be empty"):
        wrap_program(b"")

    with pytest.raises(ContainerError, match="Empty code section"):
        unwrap_program(make_container(code=b""))
