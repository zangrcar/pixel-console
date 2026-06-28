from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageOps


ALGORITHMS = {
    "nearest": Image.Resampling.NEAREST,
    "bilinear": Image.Resampling.BILINEAR,
    "bicubic": Image.Resampling.BICUBIC,
    "lanczos": Image.Resampling.LANCZOS,
}


def otsu_threshold(img: Image.Image) -> int:
    hist = img.histogram()
    total = sum(hist)

    sum_total = sum(i * hist[i] for i in range(256))
    sum_bg = 0
    weight_bg = 0
    max_variance = 0
    threshold = 128

    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue

        weight_fg = total - weight_bg
        if weight_fg == 0:
            break

        sum_bg += t * hist[t]

        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg

        variance = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2

        if variance > max_variance:
            max_variance = variance
            threshold = t

    return threshold


def crop_to_content(img: Image.Image) -> Image.Image:
    # Assumes light background. Finds non-white-ish content.
    gray = img.convert("L")
    mask = gray.point(lambda p: 255 if p < 250 else 0)
    bbox = mask.getbbox()

    if bbox is None:
        return img

    return img.crop(bbox)


def prepare_image(
    path: Path,
    width: int,
    height: int,
    threshold: int | None,
    algorithm: str,
    invert: bool,
    crop: bool,
    dither: bool,
) -> Image.Image:
    img = Image.open(path).convert("L")

    if crop:
        img = crop_to_content(img)

    img = img.resize((width, height), ALGORITHMS[algorithm])

    if threshold is None:
        threshold = otsu_threshold(img)

    if dither:
        # Floyd-Steinberg dithering
        img = img.convert("1")
    else:
        img = img.point(lambda p: 255 if p >= threshold else 0).convert("1")

    if invert:
        img = ImageOps.invert(img.convert("L")).convert("1")

    return img


def image_to_frame(img: Image.Image) -> bytes:
    width, height = img.size
    out = bytearray()
    bytes_per_row = (width + 7) // 8

    for y in range(height):
        for byte_col in range(bytes_per_row):
            value = 0

            for bit in range(8):
                x = byte_col * 8 + bit

                if x >= width:
                    continue

                # In mode "1", pixel is 255 for white and 0 for black.
                # Your framebuffer draws 1 bits as white pixels.
                if img.getpixel((x, y)) != 0:
                    value |= 1 << (7 - bit)

            out.append(value)

    return bytes(out)


def format_bytes(data: bytes) -> str:
    return "\n".join(f"            0b{byte:08b}," for byte in data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PNG to Pixel Console Sprite")
    parser.add_argument("image", help="PNG filename inside assets/")
    parser.add_argument("name", help="Sprite variable name, e.g. CAT")
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)

    parser.add_argument("--threshold", type=int, default=None)
    parser.add_argument("--algorithm", choices=ALGORITHMS.keys(), default="nearest")
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--crop", action="store_true")
    parser.add_argument("--dither", action="store_true")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--preview-scale", type=int, default=16)

    args = parser.parse_args()

    path = Path.cwd() / "assets" / args.image

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    img = prepare_image(
        path=path,
        width=args.width,
        height=args.height,
        threshold=args.threshold,
        algorithm=args.algorithm,
        invert=args.invert,
        crop=args.crop,
        dither=args.dither,
    )

    if args.preview:
        preview_dir = Path.cwd() / "output" / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)

        preview_path = preview_dir / f"{args.name.lower()}_{args.width}x{args.height}.png"
        preview = img.resize(
            (args.width * args.preview_scale, args.height * args.preview_scale),
            Image.Resampling.NEAREST,
        )
        preview.save(preview_path)
        print(f"Saved preview: {preview_path}")

    frame = image_to_frame(img)

    print("from src.sprite import Sprite")
    print()
    print(f"{args.name} = Sprite(")
    print(f"    width={args.width},")
    print(f"    height={args.height},")
    print("    frame_count=1,")
    print("    frames=[")
    print("        bytes([")
    print(format_bytes(frame))
    print("        ]),")
    print("    ]")
    print(")")


if __name__ == "__main__":
    main()