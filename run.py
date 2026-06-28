from __future__ import annotations

import argparse
from pathlib import Path

from src.assembler import assemble_file
from src.vm import PixelVM


def resolve_input_and_output(input_arg: str, output_arg: str | None = None) -> tuple[Path, Path]:
    if input_arg.endswith(".pxla"):
        input_path = Path(input_arg)
    else:
        input_path = Path("prog") / f"{input_arg}.pxla"

    if not input_path.is_absolute():
        input_path = Path.cwd() / input_path

    if output_arg is None:
        output_dir = Path.cwd() / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}.bin"
    else:
        output_path = Path(output_arg)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path

    return input_path, output_path


def build_and_run(input_path: Path, output_path: Path | None = None) -> None:
    if output_path is None:
        output_path = Path.cwd() / "output" / f"{input_path.stem}.bin"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    assemble_file(str(input_path), str(output_path))

    with output_path.open("rb") as handle:
        code = handle.read()

    vm = PixelVM()
    vm.run(code)


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble and run a Pixel Console program")
    parser.add_argument("input", help="Program name or path to the .pxla source file")
    parser.add_argument("--output", help="Optional output path for the compiled .bin file")
    args = parser.parse_args()

    input_path, output_path = resolve_input_and_output(args.input, args.output)
    build_and_run(input_path, output_path)


if __name__ == "__main__":
    main()
