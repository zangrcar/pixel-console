from src.assembler import assemble_text
from src.vm import PixelVM


def test_move_instruction_runs():
    code = assemble_text("""
origin 10 10
move -2 3
pset 0 0
end
""")

    vm = PixelVM()
    vm.run(code)

    assert vm.fb.pixels[13][8] == 1