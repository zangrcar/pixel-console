from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.font import FONTS
from src.framebuffer import FrameBuffer


OUTPUT_DIR = ROOT / "output" / "font_preview"
CONTACT_SHEET = OUTPUT_DIR / "font_contact_sheet.png"


def make_previews() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    samples = (
        b"ABC \x80\x81\x82",
        b"abc \x83\x84\x85",
        b"0123456789!?",
    )

    for font_id, font in FONTS.items():
        for scale in range(1, 5):
            fb = FrameBuffer()
            fb.clear(0)

            if scale == 1:
                for line, sample in enumerate(samples):
                    fb.displayText(
                        0,
                        line * (font.height + font.line_spacing),
                        sample,
                        font_id=font_id,
                        scale=scale,
                    )
            else:
                fb.displayText(
                    0,
                    0,
                    b"Aa0?\x80\x83",
                    font_id=font_id,
                    scale=scale,
                )

            path = OUTPUT_DIR / f"font_{font_id}_{font.name.lower()}_scale_{scale}.png"
            fb.save_png(path, scale=4)
            paths.append(path)

    return paths


def make_contact_sheet(paths: list[Path]) -> Path:
    images = [Image.open(path) for path in paths]
    cell_width, cell_height = images[0].size
    sheet = Image.new("1", (cell_width * 4, cell_height * 5), 0)

    for index, image in enumerate(images):
        column = index % 4
        row = index // 4
        sheet.paste(image, (column * cell_width, row * cell_height))

    sheet.save(CONTACT_SHEET)
    return CONTACT_SHEET


def main() -> None:
    paths = make_previews()
    contact_sheet = make_contact_sheet(paths)

    for path in paths:
        print(f"Saved {path}")

    print()
    print(f"Generated {len(paths)} font previews")
    print(f"Contact sheet: {contact_sheet}")


if __name__ == "__main__":
    main()
