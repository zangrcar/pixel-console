from __future__ import annotations

import math

from src.sprite_cat import BUILTIN_SPRITES as _CAT_SPRITES
from src.sprite_cat import SPRITE_NAMES as _CAT_SPRITE_NAMES


class Sprite:
    def __init__(self, width, height, frame_count, frames):
        self.width = width
        self.height = height
        self.frame_count = frame_count
        self.frames = frames


def _b(hex_string):
    return bytes.fromhex(hex_string)


def _clone(sprite):
    return Sprite(sprite.width, sprite.height, sprite.frame_count, list(sprite.frames))


def _rows(height):
    return [0 for _ in range(height)]


def _set(rows, width, height, x, y, value=1):
    x = int(round(x))
    y = int(round(y))

    if not (0 <= x < width and 0 <= y < height):
        return

    mask = 1 << (width - 1 - x)

    if value:
        rows[y] |= mask
    else:
        rows[y] &= ~mask


def _get(rows, width, height, x, y):
    if not (0 <= x < width and 0 <= y < height):
        return 0

    return 1 if rows[y] & (1 << (width - 1 - x)) else 0


def _pack(rows, width, height):
    bytes_per_row = (width + 7) // 8
    out = bytearray(bytes_per_row * height)

    for y in range(height):
        for x in range(width):
            if _get(rows, width, height, x, y):
                out[y * bytes_per_row + (x // 8)] |= 1 << (7 - (x % 8))

    return bytes(out)


def _frame(width, height, draw):
    rows = _rows(height)
    draw(rows, width, height)
    return _pack(rows, width, height)


def _sprite(width, height, drawers):
    frames = [_frame(width, height, draw) for draw in drawers]
    return Sprite(width, height, len(frames), frames)


def _line(rows, width, height, x0, y0, x1, y1):
    x0 = int(round(x0))
    y0 = int(round(y0))
    x1 = int(round(x1))
    y1 = int(round(y1))

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        _set(rows, width, height, x0, y0)

        if x0 == x1 and y0 == y1:
            return

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x0 += sx

        if e2 < dx:
            err += dx
            y0 += sy


def _rect(rows, width, height, x, y, w, h):
    for px in range(x, x + w):
        _set(rows, width, height, px, y)
        _set(rows, width, height, px, y + h - 1)

    for py in range(y, y + h):
        _set(rows, width, height, x, py)
        _set(rows, width, height, x + w - 1, py)


def _frect(rows, width, height, x, y, w, h):
    for py in range(y, y + h):
        for px in range(x, x + w):
            _set(rows, width, height, px, py)


def _ellipse(rows, width, height, cx, cy, rx, ry, filled=True):
    x0 = int(math.floor(cx - rx - 1))
    x1 = int(math.ceil(cx + rx + 1))
    y0 = int(math.floor(cy - ry - 1))
    y1 = int(math.ceil(cy + ry + 1))

    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if rx <= 0 or ry <= 0:
                continue

            value = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2

            if filled:
                if value <= 1.0:
                    _set(rows, width, height, x, y)
            elif 0.72 <= value <= 1.18:
                _set(rows, width, height, x, y)


def _star(rows, width, height, cx, cy, radius=3):
    _set(rows, width, height, cx, cy)

    for step in range(1, radius + 1):
        _set(rows, width, height, cx - step, cy)
        _set(rows, width, height, cx + step, cy)
        _set(rows, width, height, cx, cy - step)
        _set(rows, width, height, cx, cy + step)

    if radius >= 2:
        _set(rows, width, height, cx - 1, cy - 1)
        _set(rows, width, height, cx + 1, cy - 1)
        _set(rows, width, height, cx - 1, cy + 1)
        _set(rows, width, height, cx + 1, cy + 1)


def _polygon(rows, width, height, points):
    min_x = int(math.floor(min(point[0] for point in points)))
    max_x = int(math.ceil(max(point[0] for point in points)))
    min_y = int(math.floor(min(point[1] for point in points)))
    max_y = int(math.ceil(max(point[1] for point in points)))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            px = x + 0.5
            py = y + 0.5
            inside = False
            previous = points[-1]

            for current in points:
                x0, y0 = previous
                x1, y1 = current

                if (y0 > py) != (y1 > py):
                    crossing = (x1 - x0) * (py - y0) / (y1 - y0) + x0
                    if px < crossing:
                        inside = not inside

                previous = current

            if inside:
                _set(rows, width, height, x, y)


def _five_point_star(rows, width, height, cx, cy, radius, rotation=-math.pi / 2):
    points = []

    for index in range(10):
        angle = rotation + index * math.pi / 5
        point_radius = radius if index % 2 == 0 else radius * 0.42
        points.append(
            (
                cx + math.cos(angle) * point_radius,
                cy + math.sin(angle) * point_radius,
            )
        )

    _polygon(rows, width, height, points)


def _heart_pixel(x, y, cx, cy, size, scale):
    # Normalize the classic implicit heart curve to a centered square.  Its
    # natural bounds are asymmetric, so the vertical offset preserves both
    # rounded lobes and the bottom point instead of clipping the top notch.
    x_unit = size * scale / 2.30
    y_unit = size * scale / 2.26
    nx = ((x + 0.5) - cx) / x_unit
    ny = (cy - (y + 0.5)) / y_unit + 0.118
    return (nx * nx + ny * ny - 1) ** 3 - nx * nx * ny ** 3 <= 0


def _heart(rows, width, height, cx, cy, size, scale=1.0, outline=False):
    size = max(4.0, float(size))
    radius = size * scale * 0.55
    x0 = int(math.floor(cx - radius - 1))
    x1 = int(math.ceil(cx + radius + 1))
    y0 = int(math.floor(cy - radius - 1))
    y1 = int(math.ceil(cy + radius + 1))
    top_y = None

    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            outer = _heart_pixel(x, y, cx, cy, size, scale)

            if not outer:
                continue

            if top_y is None or y < top_y:
                top_y = y

            if not outline:
                _set(rows, width, height, x, y)
                continue

            border = max(1.2, min(3.0, size * 0.075))
            inner_scale = max(0.2, scale - border * 2.30 / size)
            inner = _heart_pixel(x, y, cx, cy, size, inner_scale)

            if not inner:
                _set(rows, width, height, x, y)

    if not outline and top_y is not None:
        center_left = int(math.floor(cx - 0.5))
        center_right = int(math.ceil(cx - 0.5))

        if _heart_pixel(center_left, top_y, cx, cy, size, scale):
            _set(rows, width, height, center_left, top_y, 0)
            _set(rows, width, height, center_right, top_y, 0)


def _draw_text(rows, width, height, text, x, y, scale=1):
    cursor = int(x)

    for char in text.upper():
        glyph = _FONT.get(char, _FONT[" "])
        glyph_width = len(glyph[0])

        for gy, row in enumerate(glyph):
            for gx, value in enumerate(row):
                if value != "1":
                    continue

                _frect(
                    rows,
                    width,
                    height,
                    cursor + gx * scale,
                    y + gy * scale,
                    scale,
                    scale,
                )

        cursor += (glyph_width + 1) * scale


def _text_width(text, scale=1):
    total = 0

    for char in text.upper():
        total += len(_FONT.get(char, _FONT[" "])[0]) + 1

    return max(0, total - 1) * scale


_FONT = {
    " ": ("000", "000", "000", "000", "000", "000", "000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "11100"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "01010", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
}


def _sparkle_set(rows, width, height, frame, seed=0):
    points = [
        (width * 0.18, height * 0.18),
        (width * 0.82, height * 0.20),
        (width * 0.72, height * 0.78),
    ]
    cx, cy = points[(frame + seed) % len(points)]
    _star(rows, width, height, int(cx), int(cy), max(1, min(width, height) // 14))


def _make_heart_sprite(size, style, seed):
    width = size
    height = size

    def drawer(frame):
        def draw(rows, width, height):
            scales = [0.70, 0.98, 0.84] if size <= 12 else [0.84, 0.94, 0.89]
            scale = scales[frame % 3]
            outline = style == "outline"
            _heart(rows, width, height, width / 2, height / 2, size * 0.94, scale, outline)

            if style == "sparkle":
                _sparkle_set(rows, width, height, frame, seed)

        return draw

    return _sprite(width, height, [drawer(0), drawer(1), drawer(2)])


def _make_double_heart(size, seed):
    def drawer(frame):
        def draw(rows, width, height):
            pulse = [0.84, 0.96, 0.90][frame % 3]
            _heart(rows, width, height, width * 0.38, height * 0.57, size * 0.58, pulse)
            _heart(rows, width, height, width * 0.65, height * 0.38, size * 0.48, 1.80 - pulse)
            _sparkle_set(rows, width, height, frame, seed)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_confetti_burst(size):
    def drawer(frame):
        def draw(rows, width, height):
            cx = width / 2
            cy = height / 2
            radius = size * (0.08 + frame * 0.13)
            piece_length = max(1, size // 12)

            for index in range(10):
                angle = index * math.tau / 10 + (index % 2) * 0.16
                x = int(round(cx + math.cos(angle) * radius))
                y = int(round(cy + math.sin(angle) * radius))
                kind = index % 4

                if kind == 0:
                    _frect(rows, width, height, x, y, max(1, size // 16), max(1, size // 16))
                elif kind == 1:
                    _line(rows, width, height, x, y, x + piece_length, y - piece_length)
                elif kind == 2:
                    _line(rows, width, height, x, y, x + piece_length, y + piece_length)
                else:
                    _line(rows, width, height, x, y - piece_length, x, y + piece_length)

            if frame == 0:
                _frect(rows, width, height, int(cx) - 1, int(cy) - 1, 3, 3)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2), drawer(3)])


def _make_single_star(size):
    def drawer(frame):
        def draw(rows, width, height):
            scales = [0.72, 0.88, 1.0, 0.82]
            _five_point_star(
                rows,
                width,
                height,
                width / 2,
                height / 2,
                size * 0.44 * scales[frame],
            )

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2), drawer(3)])


def _make_star_cluster(size):
    stars = [
        (0.50, 0.52, 0.25),
        (0.23, 0.28, 0.12),
        (0.76, 0.23, 0.10),
        (0.78, 0.73, 0.14),
        (0.20, 0.76, 0.08),
    ]

    def drawer(frame):
        def draw(rows, width, height):
            pulses = [0.82, 0.94, 1.0, 0.88]

            for index, (x_ratio, y_ratio, radius_ratio) in enumerate(stars):
                pulse = pulses[(frame + index) % len(pulses)]
                _five_point_star(
                    rows,
                    width,
                    height,
                    width * x_ratio,
                    height * y_ratio,
                    size * radius_ratio * pulse,
                )

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2), drawer(3)])


def _make_nested_hearts(size, ring_ratios):
    def drawer(frame):
        def draw(rows, width, height):
            pulse = [0.91, 1.0, 0.95][frame]

            for ratio in ring_ratios:
                _heart(
                    rows,
                    width,
                    height,
                    width / 2,
                    height / 2,
                    size * ratio,
                    pulse,
                    outline=True,
                )

            center_ratio = max(0.12, ring_ratios[-1] * 0.48)
            _heart(
                rows,
                width,
                height,
                width / 2,
                height / 2,
                size * center_ratio,
                pulse,
            )

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_banner(width, height, text="", style="heart"):
    def drawer(frame):
        def draw(rows, width, height):
            y = [3, 4, 2][frame]
            banner_h = height - 2 * y
            _rect(rows, width, height, 7, y, width - 14, banner_h)
            _line(rows, width, height, 7, y, 1, y + 4)
            _line(rows, width, height, 1, y + 4, 6, height // 2)
            _line(rows, width, height, 6, height // 2, 1, height - y - 4)
            _line(rows, width, height, 1, height - y - 4, 7, height - y - 1)
            _line(rows, width, height, width - 8, y, width - 2, y + 4)
            _line(rows, width, height, width - 2, y + 4, width - 7, height // 2)
            _line(rows, width, height, width - 7, height // 2, width - 2, height - y - 4)
            _line(rows, width, height, width - 2, height - y - 4, width - 8, height - y - 1)

            if style == "heart":
                heart_scale = [0.78, 0.92, 0.84][frame]
                _heart(rows, width, height, 12, height / 2, 9, heart_scale)
                _heart(rows, width, height, width - 13, height / 2, 9, heart_scale)
                if not text:
                    for x in range(24 + frame * 2, width - 20, 16):
                        _heart(rows, width, height, x, y + 2, 5, 0.76)
                        _heart(rows, width, height, x + 8, height - y - 3, 5, 0.76)
            elif style == "sparkle":
                _star(rows, width, height, 13, height // 2, 1 + frame % 2)
                _star(rows, width, height, width - 14, height // 2, 2 - frame % 2)
                if not text:
                    for x in range(28 + frame * 4, width - 24, 24):
                        _star(rows, width, height, x, y + 3, 1)
                        _star(rows, width, height, width - x, height - y - 4, 1)
            else:
                for offset in range(3):
                    _line(rows, width, height, 11 + offset, y + 3, 15 + offset, height - y - 4)
                    _line(rows, width, height, width - 12 - offset, y + 3, width - 16 - offset, height - y - 4)

            if text:
                scale = 2 if _text_width(text, 2) <= width - 30 else 1
                tw = _text_width(text, scale)
                _draw_text(rows, width, height, text, (width - tw) // 2, (height - 7 * scale) // 2, scale)

        return draw

    return _sprite(width, height, [drawer(0), drawer(1), drawer(2)])


def _make_gift(size):
    def drawer(frame):
        def draw(rows, width, height):
            box = int(size * 0.58)
            x = (width - box) // 2
            y = int(height * 0.38)
            _rect(rows, width, height, x, y, box, box)
            _line(rows, width, height, width // 2, y, width // 2, y + box - 1)
            _line(rows, width, height, x, y + box // 3, x + box - 1, y + box // 3)
            _ellipse(rows, width, height, width * 0.42 - frame, y - 2, size * 0.12, size * 0.08, filled=False)
            _ellipse(rows, width, height, width * 0.58 + frame, y - 2, size * 0.12, size * 0.08, filled=False)
            _heart(rows, width, height, width // 2, y + box // 2, max(6, size // 5), 0.85 + frame * 0.05)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_rose_bouquet(size):
    def drawer(frame):
        def draw(rows, width, height):
            bottom = int(height * 0.83)
            centers = [
                (width * 0.34, height * 0.31 + frame),
                (width * 0.50, height * 0.23),
                (width * 0.66, height * 0.32 - frame),
            ]

            for cx, cy in centers:
                _line(rows, width, height, width // 2, bottom, cx, cy + size * 0.10)
                _heart(rows, width, height, cx, cy, max(8, size * 0.22), 0.92 + frame * 0.04, outline=frame == 0)

            _line(rows, width, height, width * 0.38, bottom - 4, width * 0.62, bottom - 4)
            _line(rows, width, height, width * 0.38, bottom - 4, width * 0.50, bottom + 3)
            _line(rows, width, height, width * 0.62, bottom - 4, width * 0.50, bottom + 3)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_ring_box(size):
    def drawer(frame):
        def draw(rows, width, height):
            _rect(rows, width, height, width // 4, height // 2, width // 2, height // 4)
            _line(rows, width, height, width // 4, height // 2, width // 2, height // 3)
            _line(rows, width, height, width * 3 // 4 - 1, height // 2, width // 2, height // 3)
            _ellipse(rows, width, height, width // 2, height // 3 - frame, size * 0.16, size * 0.16, filled=False)
            _star(rows, width, height, width // 2 + size // 6, height // 3 - size // 8, 1 + frame)
            _heart(rows, width, height, width // 2, height * 0.66, max(7, size * 0.20), 0.85 + frame * 0.05)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_envelope(size):
    def drawer(frame):
        def draw(rows, width, height):
            x = width // 6
            y = height // 3
            w = width * 2 // 3
            h = height // 3
            _rect(rows, width, height, x, y, w, h)
            _line(rows, width, height, x, y, x + w // 2, y + h // 2 + frame)
            _line(rows, width, height, x + w - 1, y, x + w // 2, y + h // 2 + frame)
            _line(rows, width, height, x, y + h - 1, x + w // 2, y + h // 2 + frame)
            _line(rows, width, height, x + w - 1, y + h - 1, x + w // 2, y + h // 2 + frame)
            _heart(rows, width, height, width // 2, y + h // 2, max(6, size * 0.18), 0.82 + frame * 0.08)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_firework(size):
    def drawer(frame):
        def draw(rows, width, height):
            cx = width // 2
            cy = height // 2
            radius = size * (0.20 + frame * 0.11)

            for spoke in range(12):
                angle = spoke * math.tau / 12
                inner = radius * 0.45
                _line(
                    rows,
                    width,
                    height,
                    cx + math.cos(angle) * inner,
                    cy + math.sin(angle) * inner,
                    cx + math.cos(angle) * radius,
                    cy + math.sin(angle) * radius,
                )

            _heart(rows, width, height, cx, cy, max(6, size * 0.22), 0.85 + frame * 0.04)
            _star(rows, width, height, int(width * 0.23), int(height * (0.25 + frame * 0.08)), 1)
            _star(rows, width, height, int(width * 0.76), int(height * (0.78 - frame * 0.06)), 1)

        return draw

    return _sprite(size, size, [drawer(0), drawer(1), drawer(2)])


def _make_background(kind):
    width = 128
    height = 64

    def drawer(frame):
        def draw(rows, width, height):
            phase = frame * 4
            _rect(rows, width, height, 0, 0, width, height)
            _rect(rows, width, height, 3, 3, width - 6, height - 6)

            if kind == "heart":
                for x in range(-8 + phase, width + 8, 16):
                    _heart(rows, width, height, x, 4, 8, 0.8 + frame * 0.05)
                    _heart(rows, width, height, x + 8, height - 5, 8, 1.0 - frame * 0.04)
                for y in range(10 + phase // 2, height - 6, 14):
                    _heart(rows, width, height, 4, y, 8, 0.86)
                    _heart(rows, width, height, width - 5, y + 6, 8, 0.96)

            elif kind == "star":
                for x in range(6 + phase, width, 14):
                    _star(rows, width, height, x, 4, 2 + frame % 2)
                    _star(rows, width, height, width - x, height - 5, 1 + frame % 2)
                for y in range(8, height - 5, 12):
                    _star(rows, width, height, 5, y + frame % 3, 2)
                    _star(rows, width, height, width - 6, y - frame % 3, 2)

            elif kind == "ribbon":
                for x in range(frame * 2, width, 8):
                    if (x // 8 + frame) % 2 == 0:
                        _frect(rows, width, height, x, 1, 5, 3)
                        _frect(rows, width, height, x + 3, height - 4, 5, 3)
                for y in range(frame * 2, height, 8):
                    if (y // 8 + frame) % 2 == 0:
                        _frect(rows, width, height, 1, y, 3, 5)
                        _frect(rows, width, height, width - 4, y + 3, 3, 5)
                for cx, cy in [(10, 10), (width - 11, 10), (10, height - 11), (width - 11, height - 11)]:
                    _line(rows, width, height, cx - 5, cy - 3, cx, cy)
                    _line(rows, width, height, cx - 5, cy + 3, cx, cy)
                    _line(rows, width, height, cx + 5, cy - 3, cx, cy)
                    _line(rows, width, height, cx + 5, cy + 3, cx, cy)
                    _frect(rows, width, height, cx - 1, cy - 1, 3, 3)

            else:
                for x in range(4, width - 4, 10):
                    y = 4 + ((x + phase) // 10) % 3
                    _line(rows, width, height, x, y, x + 3, y + frame)
                    _line(rows, width, height, x, height - y - 1, x + 3, height - y - frame - 1)
                for y in range(8, height - 8, 8):
                    _set(rows, width, height, 3 + frame, y)
                    _set(rows, width, height, width - 4 - frame, y + 3)
                    _line(rows, width, height, 1, y, 5, y + 2)
                    _line(rows, width, height, width - 2, y + 2, width - 6, y)

        return draw

    return _sprite(width, height, [drawer(0), drawer(1), drawer(2)])


def _make_confetti_background():
    width = 128
    height = 64

    def drawer(frame):
        def draw(rows, width, height):
            for index in range(46):
                base_x = (index * 31 + index * index * 3) % width
                base_y = (index * 17 + (index % 6) * 7) % height
                drift_x = frame * ((index % 3) - 1)
                drift_y = frame * (2 + index % 3)
                x = (base_x + drift_x) % width
                y = (base_y + drift_y) % height
                kind = index % 5

                if kind == 0:
                    _frect(rows, width, height, x, y, 2, 2)
                elif kind == 1:
                    _line(rows, width, height, x, y, x + 3, y + 1)
                elif kind == 2:
                    _line(rows, width, height, x, y, x + 2, y - 2)
                elif kind == 3:
                    _line(rows, width, height, x, y - 2, x, y + 2)
                else:
                    _star(rows, width, height, x, y, 1)

        return draw

    return _sprite(width, height, [drawer(0), drawer(1), drawer(2), drawer(3)])


def _build_anniversary_sprites():
    sprites = []

    for size in [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 56, 64]:
        sprites.append((f"HEART_SOLID_{size:02}", _make_heart_sprite(size, "solid", size)))

    for size in [16, 20, 24, 28, 32, 40, 48, 56, 64]:
        sprites.append((f"HEART_OUTLINE_{size:02}", _make_heart_sprite(size, "outline", size + 3)))

    for size in [16, 20, 24, 28, 32, 40, 48, 64]:
        sprites.append((f"HEART_SPARKLE_{size:02}", _make_heart_sprite(size, "sparkle", size + 7)))

    for size in [24, 28, 32, 40, 48]:
        sprites.append((f"DOUBLE_HEART_{size:02}", _make_double_heart(size, size + 11)))

    sprites.extend(
        [
            ("CONFETTI_BURST_16", _make_confetti_burst(16)),
            ("CONFETTI_BURST_24", _make_confetti_burst(24)),
            ("STAR_SINGLE_32", _make_single_star(32)),
            ("STAR_CLUSTER_48", _make_star_cluster(48)),
        ]
    )

    sprites.extend(
        [
            ("NESTED_HEART_32", _make_nested_hearts(32, [0.88, 0.58])),
            ("NESTED_HEART_48", _make_nested_hearts(48, [0.90, 0.70, 0.50, 0.32])),
            ("NESTED_HEART_64", _make_nested_hearts(64, [0.90, 0.74, 0.58, 0.42, 0.27])),
            ("LOVE_BANNER_96X24", _make_banner(96, 24, "LOVE", "heart")),
            ("FOREVER_BANNER_112X24", _make_banner(112, 24, "FOREVER", "heart")),
            ("TOGETHER_BANNER_128X24", _make_banner(128, 24, "TOGETHER", "ribbon")),
            ("HAPPY_BANNER_96X24", _make_banner(96, 24, "HAPPY", "sparkle")),
            ("CHEERS_BANNER_96X24", _make_banner(96, 24, "CHEERS", "ribbon")),
            ("CELEBRATE_BANNER_128X24", _make_banner(128, 24, "CELEBRATE", "sparkle")),
            ("HEART_TEXT_BANNER_128X24", _make_banner(128, 24, style="heart")),
            ("RIBBON_TEXT_BANNER_128X24", _make_banner(128, 24, style="ribbon")),
            ("SPARKLE_TEXT_BANNER_128X24", _make_banner(128, 24, style="sparkle")),
            ("NESTED_HEART_40", _make_nested_hearts(40, [0.88, 0.64, 0.42])),
            ("GIFT_32", _make_gift(32)),
            ("ROSE_BOUQUET_32", _make_rose_bouquet(32)),
            ("RING_BOX_32", _make_ring_box(32)),
            ("ENVELOPE_HEART_32", _make_envelope(32)),
            ("FIREWORK_HEART_40", _make_firework(40)),
            ("BG_HEART_BORDER_128X64", _make_background("heart")),
            ("BG_STAR_BORDER_128X64", _make_background("star")),
            ("BG_RIBBON_BORDER_128X64", _make_background("ribbon")),
            ("BG_CONFETTI_FULL_128X64", _make_confetti_background()),
        ]
    )

    if len(sprites) != 62:
        raise RuntimeError(f"Expected 62 anniversary sprites, got {len(sprites)}")

    return sprites


_SPRITE_ITEMS = []

for index in range(len(_CAT_SPRITE_NAMES)):
    name = _CAT_SPRITE_NAMES[index]
    # Preserve every source frame, including intentional animation holds.
    _SPRITE_ITEMS.append((name, _clone(_CAT_SPRITES[index])))

_SPRITE_ITEMS.extend(_build_anniversary_sprites())

if len(_SPRITE_ITEMS) != 128:
    raise RuntimeError(f"sprite_codex must define 128 sprites, got {len(_SPRITE_ITEMS)}")

SPRITE_NAMES = {}
BUILTIN_SPRITES = []

for index, (name, sprite) in enumerate(_SPRITE_ITEMS):
    globals()[name] = sprite
    SPRITE_NAMES[index] = name
    BUILTIN_SPRITES.append(sprite)

SPRITE_IDS = {name: index for index, name in SPRITE_NAMES.items()}

SPRITE_IDS.update(
    {
        "CAT": SPRITE_IDS["PIXEL_CAT_00"],
        "PIXEL_CAT": SPRITE_IDS["PIXEL_CAT_00"],
        "HEART": SPRITE_IDS["HEART_SOLID_32"],
        "LOVE": SPRITE_IDS["HEART_SOLID_32"],
        "BIG_HEART": SPRITE_IDS["HEART_SOLID_64"],
        "SMALL_HEART": SPRITE_IDS["HEART_SOLID_16"],
        "ANNIVERSARY": SPRITE_IDS["NESTED_HEART_48"],
        "BANNER": SPRITE_IDS["HEART_TEXT_BANNER_128X24"],
        "LOVE_BANNER": SPRITE_IDS["LOVE_BANNER_96X24"],
        "STAR": SPRITE_IDS["STAR_SINGLE_32"],
        "CONFETTI": SPRITE_IDS["CONFETTI_BURST_24"],
        "BACKGROUND_HEARTS": SPRITE_IDS["BG_HEART_BORDER_128X64"],
        "BACKGROUND_STARS": SPRITE_IDS["BG_STAR_BORDER_128X64"],
        "BACKGROUND_CONFETTI": SPRITE_IDS["BG_CONFETTI_FULL_128X64"],
    }
)
