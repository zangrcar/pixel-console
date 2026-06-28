from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.assembler import assemble_text
from src.container import wrap_program, unwrap_program
from src.inspect import inspect_bytes
from src.vm import PixelVM
from run import load_program_sprites, resolve_input_and_output
from src.validator import validate_program


def preview(input_arg: str, output_arg: str | None = None) -> None:
    input_path, output_path = resolve_input_and_output(input_arg, output_arg)

    preview_dir = Path.cwd() / "output" / f"{input_path.stem}_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    source = input_path.read_text(encoding="utf-8")
    code = assemble_text(source)

    sprites = load_program_sprites(input_path)
    program = wrap_program(code, sprites=sprites)

    output_path.write_bytes(program)

    print(f"Wrote {len(program)} bytes to {output_path}")
    inspect_bytes(program)

    loaded_code, loaded_sprites = unwrap_program(program)
    
    validate_program(loaded_code, loaded_sprites)

    frames = []

    def on_frame(framebuffer):
        frames.append(framebuffer)

    vm = PixelVM(card_sprites=loaded_sprites, on_frame=on_frame)
    vm.run(loaded_code)

    for index, framebuffer in enumerate(frames):
        path = preview_dir / f"frame_{index:04}.png"
        framebuffer.save_png(path, scale=8)

    print()
    print(f"Preview frames: {len(frames)}")
    print(f"Saved to: {preview_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a Pixel Console program")
    parser.add_argument("input", help="Program name or path to .pxla file")
    parser.add_argument("--output", help="Optional compiled .bin output path")
    args = parser.parse_args()

    preview(args.input, args.output)


if __name__ == "__main__":
    main()