from src.container import wrap_program, unwrap_program


def test_wrap_unwrap_program():
    code = bytes([0x02, 0x00, 0x00])
    program = wrap_program(code)

    loaded_code, loaded_sprites = unwrap_program(program)

    assert loaded_code == code
    assert loaded_sprites == []


def test_crc_detects_corruption():
    code = bytes([0x02, 0x00, 0x00])
    program = bytearray(wrap_program(code))

    program[-1] ^= 0xFF

    try:
        unwrap_program(bytes(program))
        assert False
    except Exception:
        assert True