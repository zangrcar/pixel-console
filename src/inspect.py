from __future__ import annotations

import argparse
from pathlib import Path

from src.container import (
    HEADER_SIZE,
    MAGIC,
    MAX_NTAG216_BYTES,
    TOTAL_LENGTH_OFFSET,
    VERSION_OFFSET,
    CRCError,
    unwrap_program,
)


def _declared_size(data: bytes) -> int | None:
    if len(data) < HEADER_SIZE or data[:4] != MAGIC:
        return None

    return int.from_bytes(
        data[TOTAL_LENGTH_OFFSET:TOTAL_LENGTH_OFFSET + 2],
        "little",
    )

def inspect_bytes(data):
    data = bytes(data)
    declared_size = _declared_size(data)
    used_size = declared_size if declared_size is not None else len(data)
    fits = used_size <= MAX_NTAG216_BYTES and len(data) <= MAX_NTAG216_BYTES

    print(f"Total size: {used_size} bytes")

    if len(data) != used_size:
        print(f"Input size: {len(data)} bytes")

    print(f"Fits NTAG216: {'yes' if fits else 'no'}")
    print(f"Remaining: {max(0, MAX_NTAG216_BYTES - used_size)} bytes")

    if len(data) >= HEADER_SIZE and data[:4] == MAGIC:
        print(f"Version: {data[VERSION_OFFSET]}")

    try:
        code, sprites = unwrap_program(data)

        print()
        print("PXL1 container: yes")
        print("CRC status: ok")
        print(f"Card sprites: {len(sprites)}")
        print(f"Code size: {len(code)} bytes")

        for i, sprite in enumerate(sprites):
            print(
                f"  Sprite {128 + i}: "
                f"{sprite.width}x{sprite.height}, "
                f"{sprite.frame_count} frame(s)"
            )

    except Exception as e:
        print()
        print("PXL1 container: no")
        print(f"CRC status: {'bad' if isinstance(e, CRCError) else 'not checked'}")
        print(f"Reason: {e}")

    print()
    print("Hex:")
    hex_end = min(len(data), used_size) if used_size > 0 else len(data)
    print(data[:hex_end].hex(" "))


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a PXL1 .bin file")
    parser.add_argument("input", help="Path to a PXL1 .bin file")
    args = parser.parse_args()

    inspect_bytes(Path(args.input).read_bytes())


if __name__ == "__main__":
    main()
