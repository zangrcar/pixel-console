from src.vm import PixelVM

def test_hardcoded_program():
    code = bytes([
        0x02, 0x00,              # CLEAR 0
        0x03, 0x01,              # MODE 1
        0x12, 0, 0, 128, 64,     # RECT 0 0 128 64
        0x13, 20, 20, 30, 15,    # FRECT 20 20 30 15
        0x06, 60,                # FRAME 60
        0x00                     # END
    ])

    vm = PixelVM()
    vm.run(code)