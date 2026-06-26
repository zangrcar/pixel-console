from src.assembler import assemble_file
from src.vm import PixelVM

def test_text():
    assemble_file("prog/text.pxla", "output/text.bin")
    with open("output/text.bin", "rb") as f:
        code = f.read()

    vm = PixelVM()
    vm.run(code)