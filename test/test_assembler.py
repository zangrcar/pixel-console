from src.assembler import assemble_file
from src.vm import PixelVM

def test_assembler_hello():
    assemble_file("prog/hello.pxla", "output/hello.bin")
    with open("output/hello.bin", "rb") as f:
        code = f.read()

    vm = PixelVM()
    vm.run(code)