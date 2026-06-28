from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image


def find_project_root() -> Path:
    here = Path(__file__).resolve()

    for path in [here.parent, *here.parents, Path.cwd(), *Path.cwd().parents]:
        if (path / "src" / "sprite.py").exists():
            return path

    raise RuntimeError("Could not find project root containing src/sprite.py")


PROJECT_ROOT = find_project_root()
sys.path.insert(0, str(PROJECT_ROOT))

from src.sprite import BUILTIN_SPRITES, SPRITE_NAMES


OUTPUT_DIR = PROJECT_ROOT / "output" / "builtin_sprites"
SCALE = 8


def safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def get_sprite_name(sprite_id: int) -> str:
    if isinstance(SPRITE_NAMES, dict):
        return SPRITE_NAMES.get(sprite_id, f"SPRITE_{sprite_id}")

    if sprite_id < len(SPRITE_NAMES):
        return SPRITE_NAMES[sprite_id]

    return f"SPRITE_{sprite_id}"


def frame_to_image(sprite, frame_index: int, scale: int = SCALE) -> Image.Image:
    frame = sprite.frames[frame_index]
    width = sprite.width
    height = sprite.height
    bytes_per_row = (width + 7) // 8

    img = Image.new("1", (width, height), 0)

    for y in range(height):
        row_offset = y * bytes_per_row

        for x in range(width):
            byte = frame[row_offset + (x // 8)]
            bit_index = 7 - (x % 8)

            if byte & (1 << bit_index):
                img.putpixel((x, y), 1)

    if scale != 1:
        img = img.resize(
            (width * scale, height * scale),
            Image.Resampling.NEAREST,
        )

    return img


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0

    for sprite_id, sprite in enumerate(BUILTIN_SPRITES):
        sprite_name = safe_filename(get_sprite_name(sprite_id))

        for frame_index in range(sprite.frame_count):
            img = frame_to_image(sprite, frame_index)

            filename = f"{sprite_name}_{frame_index}.png"
            path = OUTPUT_DIR / filename
            img.save(path)

            total_files += 1
            print(f"Saved {path}")

    print()
    print(f"Exported {total_files} PNG files to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()