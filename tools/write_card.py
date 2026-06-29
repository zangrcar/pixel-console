from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.assembler import assemble_text
from src.container import wrap_program
from run import load_program_sprites, resolve_input_and_output


class NFCWriter:
    def __init__(self):
        import board
        import busio
        from adafruit_pn532.i2c import PN532_I2C

        i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(i2c, debug=False)
        self.pn532.SAM_configuration()

    def wait_for_card(self):
        while True:
            uid = self.pn532.read_passive_target(timeout=0.5)
            if uid is not None:
                return uid

    def write_ntag216_user_memory(self, data: bytes) -> None:
        if len(data) > 888:
            raise ValueError("Data too large for NTAG216")

        padded = data + bytes(888 - len(data))

        for index in range(222):
            page = 4 + index
            chunk = padded[index * 4:index * 4 + 4]

            ok = self.pn532.ntag2xx_write_block(page, chunk)

            if not ok:
                raise RuntimeError(f"Failed writing page {page}")


def build_program(input_arg: str, output_arg: str | None = None) -> bytes:
    input_path, output_path = resolve_input_and_output(input_arg, output_arg)

    source = input_path.read_text(encoding="utf-8")
    code = assemble_text(source)

    sprites = load_program_sprites(input_path)
    program = wrap_program(code, sprites=sprites)

    output_path.write_bytes(program)
    print(f"Wrote {len(program)} bytes to {output_path}")

    return program


def main() -> None:
    parser = argparse.ArgumentParser(description="Write PXLA program to NTAG216 NFC card")
    parser.add_argument("input", help="Program name or path to .pxla file")
    parser.add_argument("--output", help="Optional .bin output path")
    args = parser.parse_args()

    program = build_program(args.input, args.output)

    writer = NFCWriter()

    print("Place NFC card on reader...")
    writer.wait_for_card()

    print("Writing...")
    writer.write_ntag216_user_memory(program)

    print("Done.")


if __name__ == "__main__":
    main()