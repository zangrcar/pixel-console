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
    code = assemble_text(source, source_name=str(input_path))

    sprites = load_program_sprites(input_path)
    program = wrap_program(code, sprites=sprites)

    output_path.write_bytes(program)

    print(f"Wrote {len(program)} bytes to {output_path}")
    inspect_bytes(program)

    loaded_code, loaded_sprites = unwrap_program(program)
    
    validate_program(loaded_code, loaded_sprites)

    frames = []
    last_frame_index = None

    def on_frame(framebuffer, ticks):
        nonlocal last_frame_index
        frames.append([framebuffer, max(1, ticks)])
        last_frame_index = len(frames) - 1

    def on_wait(ticks):
        if last_frame_index is not None:
            frames[last_frame_index][1] += ticks

    vm = PixelVM(
        card_sprites=loaded_sprites,
        on_frame=on_frame,
        on_wait=on_wait,
    )
    vm.run(loaded_code, max_frames=120, max_steps=5000)

    for index, (framebuffer, ticks) in enumerate(frames):
        path = preview_dir / f"frame_{index:04}.png"
        framebuffer.save_png(path, scale=8)
        print(f"Saved {path} ({ticks} ticks)")

    print()
    print(f"Preview frames: {len(frames)}")

    if frames:
        print(f"Saved to: {preview_dir}")
    else:
        print("No frames produced. Add SHOW or FRAME instructions.")

    return frames


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a Pixel Console program")
    parser.add_argument("input", help="Program name or path to .pxla file")
    parser.add_argument("--output", help="Optional compiled .bin output path")
    args = parser.parse_args()

    preview(args.input, args.output)


if __name__ == "__main__":
    main()
