from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageSequence, ImageOps


class Sprite:
    def __init__(self, width, height, frame_count, frames):
        self.width = width
        self.height = height
        self.frame_count = frame_count
        self.frames = frames


def _b(hex_string):
    return bytes.fromhex(hex_string)


IMAGE_EXTENSIONS = {".png", ".gif", ".webp", ".bmp", ".jpg", ".jpeg"}


def safe_name(value: str) -> str:
    value = value.upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value).strip("_")
    if not value:
        value = "CAT"
    if value[0].isdigit():
        value = "CAT_" + value
    return value


def strip_color_suffix(stem: str) -> str:
    """Group files that are the same cat repeated in different color variants."""
    patterns = [
        r"([_-]?)(black|white|orange|grey|gray|brown|gold|golden|blue|red|pink|green|yellow|purple|silver)$",
        r"([_-]?)(color|colour|variant)[_-]?\d+$",
        r"([_-]?)(c|v)\d+$",
        r"([_-]?)\d+$",
    ]
    base = stem
    for pattern in patterns:
        base = re.sub(pattern, "", base, flags=re.IGNORECASE)
    return base or stem


def crop_to_content(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")

    # Prefer alpha if present. Otherwise find non-background pixels by comparing to corners.
    if alpha.getextrema() != (255, 255):
        bbox = alpha.getbbox()
        return rgba.crop(bbox) if bbox else rgba

    rgb = rgba.convert("RGB")
    corners = [rgb.getpixel((0, 0)), rgb.getpixel((rgb.width - 1, 0)), rgb.getpixel((0, rgb.height - 1)), rgb.getpixel((rgb.width - 1, rgb.height - 1))]
    bg = max(set(corners), key=corners.count)
    mask = Image.new("L", rgb.size, 0)
    pix = rgb.load()
    out = mask.load()
    tolerance = 12
    for y in range(rgb.height):
        for x in range(rgb.width):
            r, g, b = pix[x, y]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > tolerance:
                out[x, y] = 255
    bbox = mask.getbbox()
    return rgba.crop(bbox) if bbox else rgba


def pad_to_size(img: Image.Image, width: int, height: int) -> Image.Image:
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = (width - img.width) // 2
    y = (height - img.height) // 2
    out.alpha_composite(img.convert("RGBA"), (x, y))
    return out


def prepare_frame(img: Image.Image, width: int | None, height: int | None, crop: bool, invert: bool) -> Image.Image:
    rgba = img.convert("RGBA")
    if crop:
        rgba = crop_to_content(rgba)

    if width is not None and height is not None:
        rgba.thumbnail((width, height), Image.Resampling.NEAREST)
        rgba = pad_to_size(rgba, width, height)

    alpha = rgba.getchannel("A")
    gray = rgba.convert("L")

    # Treat visible non-transparent pixels as sprite pixels. This is best for colored pixel art.
    mask = Image.new("1", rgba.size, 0)
    for y in range(rgba.height):
        for x in range(rgba.width):
            if alpha.getpixel((x, y)) > 0:
                # Ignore almost-white background pixels if the image has no useful alpha.
                if alpha.getextrema() == (255, 255) and gray.getpixel((x, y)) > 245:
                    continue
                mask.putpixel((x, y), 1)

    if invert:
        mask = ImageOps.invert(mask.convert("L")).convert("1")
    return mask


def image_to_bytes(img: Image.Image) -> bytes:
    width, height = img.size
    bytes_per_row = (width + 7) // 8
    out = bytearray()

    for y in range(height):
        for byte_col in range(bytes_per_row):
            value = 0
            for bit in range(8):
                x = byte_col * 8 + bit
                if x < width and img.getpixel((x, y)) != 0:
                    value |= 1 << (7 - bit)
            out.append(value)

    return bytes(out)


def load_frames(path: Path, width: int | None, height: int | None, crop: bool, invert: bool) -> list[Image.Image]:
    with Image.open(path) as image:
        frames = []
        for frame in ImageSequence.Iterator(image):
            prepared = prepare_frame(frame, width, height, crop, invert)
            frames.append(prepared)
        return frames


def choose_one_color_variant(paths: list[Path]) -> Path:
    # Deterministic and simple: prefer names without explicit color, otherwise shortest filename.
    def score(path: Path) -> tuple[int, int, str]:
        has_color = bool(re.search(r"(black|white|orange|grey|gray|brown|gold|golden|blue|red|pink|green|yellow|purple|silver)", path.stem, re.I))
        return (1 if has_color else 0, len(path.name), path.name.lower())
    return sorted(paths, key=score)[0]


def sprite_block(name: str, frames: list[Image.Image]) -> str:
    width, height = frames[0].size
    data = [image_to_bytes(frame).hex() for frame in frames]
    lines = [
        f"{name} = Sprite(",
        f"    width={width},",
        f"    height={height},",
        f"    frame_count={len(frames)},",
        "    frames=[",
    ]
    for hex_string in data:
        lines.append(f'        _b("{hex_string}"),')
    lines.extend(["    ],", ")", ""])
    return "\n".join(lines)


def make_preview(frames: list[Image.Image], out_dir: Path, name: str, scale: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(frames):
        preview = frame.resize((frame.width * scale, frame.height * scale), Image.Resampling.NEAREST)
        preview.save(out_dir / f"{name}_{i:02}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert downloaded Pixel Cat images/GIFs into Pixel Console Sprite objects.")
    parser.add_argument("source", help="Folder containing downloaded pixel cat files")
    parser.add_argument("--output", default="pixel_cat_sprites.py", help="Output .py file")
    parser.add_argument("--width", type=int, default=None, help="Optional target sprite width")
    parser.add_argument("--height", type=int, default=None, help="Optional target sprite height")
    parser.add_argument("--no-crop", action="store_true", help="Do not crop transparent/background border")
    parser.add_argument("--invert", action="store_true", help="Invert output mask")
    parser.add_argument("--preview", action="store_true", help="Write scaled preview PNGs")
    parser.add_argument("--preview-scale", type=int, default=8)
    args = parser.parse_args()

    source = Path(args.source)
    files = [p for p in source.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS]
    if not files:
        raise SystemExit(f"No image files found in {source}")

    groups: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        groups[strip_color_suffix(path.stem)].append(path)

    blocks = [
        "from __future__ import annotations",
        "",
        "class Sprite:",
        "    def __init__(self, width, height, frame_count, frames):",
        "        self.width = width",
        "        self.height = height",
        "        self.frame_count = frame_count",
        "        self.frames = frames",
        "",
        "def _b(hex_string):",
        "    return bytes.fromhex(hex_string)",
        "",
    ]
    sprite_names: list[str] = []
    preview_root = Path(args.output).with_suffix("").parent / "pixel_cat_previews"

    for base, paths in sorted(groups.items()):
        chosen = choose_one_color_variant(paths)
        name = safe_name(base)
        frames = load_frames(chosen, args.width, args.height, not args.no_crop, args.invert)
        if not frames:
            continue
        sprite_names.append(name)
        blocks.append(f"# Source: {chosen.name}")
        blocks.append(sprite_block(name, frames))
        if args.preview:
            make_preview(frames, preview_root, name, args.preview_scale)
        print(f"{name}: {chosen.name}, {frames[0].width}x{frames[0].height}, {len(frames)} frame(s)")

    blocks.append("SPRITES = [")
    for name in sprite_names:
        blocks.append(f"    {name},")
    blocks.append("]")
    blocks.append("")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(blocks), encoding="utf-8")
    print(f"\nWrote {len(sprite_names)} sprites to {output}")
    if args.preview:
        print(f"Wrote previews to {preview_root}")


if __name__ == "__main__":
    main()
