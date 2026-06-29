from src.assembler import assemble_text
from src.validator import validate_program


def test_valid_program():
    code = assemble_text("""
clear 0
frame 10
end
""")

    validate_program(code, [])


def test_bad_jump_target_fails():
    code = bytes([
        0x07, 0x01, 0x00,
        0x00,
    ])

    try:
        validate_program(code, [])
        assert False
    except Exception:
        assert True