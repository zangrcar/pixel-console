from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.assembler import assemble_text
from src.container import TOTAL_LENGTH_OFFSET, unwrap_program, wrap_program
from src.nfc import NFCReader
from run import load_program_sprites, resolve_input_and_output


def build_program(input_arg: str, output_arg: str | None = None) -> bytes:
    input_path, output_path = resolve_input_and_output(input_arg, output_arg)

    source = input_path.read_text(encoding="utf-8")
    code = assemble_text(source, source_name=str(input_path))

    sprites = load_program_sprites(input_path)
    program = wrap_program(code, sprites=sprites)

    output_path.write_bytes(program)
    print(f"Wrote {len(program)} bytes to {output_path}")

    return program


def load_program(input_arg: str, output_arg: str | None = None) -> bytes:
    if not input_arg.lower().endswith(".bin"):
        return build_program(input_arg, output_arg)

    if output_arg is not None:
        raise ValueError("--output is only supported when building a .pxla program")

    input_path = Path(input_arg)

    if not input_path.is_absolute():
        input_path = Path.cwd() / input_path

    data = input_path.read_bytes()
    unwrap_program(data)

    used_size = int.from_bytes(
        data[TOTAL_LENGTH_OFFSET:TOTAL_LENGTH_OFFSET + 2],
        "little",
    )
    program = data[:used_size]
    print(f"Loaded {used_size} used bytes from {input_path}")

    return program


def main() -> None:
    parser = argparse.ArgumentParser(description="Write and verify a PXL1 program on NTAG216")
    parser.add_argument("input", help="Program name or path to .pxla/.bin file")
    parser.add_argument("--output", help="Optional .bin output path for .pxla input")
    args = parser.parse_args()

    program = load_program(args.input, args.output)

    reader = NFCReader()

    print("Place NFC card on reader...")
    uid = reader.wait_for_card()
    print(f"Card UID: {uid.hex().upper()}")

    print(f"Writing {len(program)} used bytes...")
    reader.write_and_verify(program)
    print(f"Verified {len(program)} bytes; PXL1 CRC OK.")

    print("Remove NFC card...")
    reader.wait_for_removal()
    print("Done.")


if __name__ == "__main__":
    main()
