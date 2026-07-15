from src import sprite_cat, sprite_codex


def test_sprite_codex_has_128_sprites_with_cat_bank_first():
    assert len(sprite_codex.BUILTIN_SPRITES) == 128

    for index in range(len(sprite_cat.BUILTIN_SPRITES)):
        codex_sprite = sprite_codex.BUILTIN_SPRITES[index]
        cat_sprite = sprite_cat.BUILTIN_SPRITES[index]

        assert sprite_codex.SPRITE_NAMES[index] == sprite_cat.SPRITE_NAMES[index]
        assert codex_sprite.width == cat_sprite.width
        assert codex_sprite.height == cat_sprite.height
        assert codex_sprite.frame_count == cat_sprite.frame_count
        assert codex_sprite.frames == cat_sprite.frames


def test_sprite_codex_frame_metadata_is_valid():
    cat_count = len(sprite_cat.BUILTIN_SPRITES)

    for index, sprite in enumerate(sprite_codex.BUILTIN_SPRITES):
        bytes_per_frame = ((sprite.width + 7) // 8) * sprite.height

        assert sprite.frame_count == len(sprite.frames)
        assert sprite.frame_count >= 2
        assert all(len(frame) == bytes_per_frame for frame in sprite.frames)

        if index >= cat_count:
            assert len(set(sprite.frames)) == sprite.frame_count


def test_sprite_codex_anniversary_sprites_are_unique_and_large():
    seen_sprites = {}

    for index in range(len(sprite_codex.BUILTIN_SPRITES)):
        sprite = sprite_codex.BUILTIN_SPRITES[index]
        name = sprite_codex.SPRITE_NAMES[index]
        signature = (sprite.width, sprite.height, tuple(sprite.frames))

        assert signature not in seen_sprites
        seen_sprites[signature] = name

        if index < len(sprite_cat.BUILTIN_SPRITES):
            continue

        if name not in {"HEART_SOLID_08", "HEART_SOLID_10", "HEART_SOLID_12", "HEART_SOLID_14"}:
            assert min(sprite.width, sprite.height) >= 16


def test_sprite_codex_heart_sizes_and_backgrounds():
    solid_heart_sizes = {
        sprite_codex.BUILTIN_SPRITES[index].width
        for index, name in sprite_codex.SPRITE_NAMES.items()
        if name.startswith("HEART_SOLID_")
    }
    backgrounds = [
        sprite_codex.BUILTIN_SPRITES[index]
        for index, name in sprite_codex.SPRITE_NAMES.items()
        if name.startswith("BG_")
    ]

    assert {8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 56, 64} <= solid_heart_sizes
    assert len(backgrounds) >= 2
    assert all(sprite.width == 128 and sprite.height == 64 for sprite in backgrounds)


def test_removed_sprites_are_replaced_with_generic_banners():
    names = set(sprite_codex.SPRITE_NAMES.values())

    assert not any("LOCK" in name or "KEY" in name or "CAKE" in name for name in names)
    assert not any("ONE_YEAR_BANNER" in name for name in names)
    assert not any("ANNIV_BADGE" in name or "DAYS_365" in name for name in names)
    assert {
        "LOVE_BANNER_96X24",
        "FOREVER_BANNER_112X24",
        "TOGETHER_BANNER_128X24",
        "HAPPY_BANNER_96X24",
        "CHEERS_BANNER_96X24",
        "CELEBRATE_BANNER_128X24",
        "HEART_TEXT_BANNER_128X24",
        "RIBBON_TEXT_BANNER_128X24",
        "SPARKLE_TEXT_BANNER_128X24",
    } <= names


def test_anniversary_badges_are_replaced_with_nested_hearts():
    names = set(sprite_codex.SPRITE_NAMES.values())

    assert {
        "NESTED_HEART_32",
        "NESTED_HEART_40",
        "NESTED_HEART_48",
        "NESTED_HEART_64",
    } <= names

    for name in [name for name in names if name.startswith("NESTED_HEART_")]:
        sprite = sprite_codex.BUILTIN_SPRITES[sprite_codex.SPRITE_IDS[name]]
        row_bytes = (sprite.width + 7) // 8
        center_x = sprite.width // 2
        center_y = sprite.height // 2

        for frame in sprite.frames:
            center_byte = frame[center_y * row_bytes + center_x // 8]
            assert center_byte & (1 << (7 - center_x % 8))


def test_arrow_hearts_are_replaced_with_stars_and_confetti():
    names = set(sprite_codex.SPRITE_NAMES.values())
    expected = {
        "CONFETTI_BURST_16": (16, 16),
        "CONFETTI_BURST_24": (24, 24),
        "STAR_SINGLE_32": (32, 32),
        "STAR_CLUSTER_48": (48, 48),
        "BG_CONFETTI_FULL_128X64": (128, 64),
    }

    assert not any(name.startswith("HEART_ARROW_") for name in names)
    assert "BG_CONFETTI_BORDER_128X64" not in names

    for name, dimensions in expected.items():
        sprite = sprite_codex.BUILTIN_SPRITES[sprite_codex.SPRITE_IDS[name]]

        assert (sprite.width, sprite.height) == dimensions
        assert sprite.frame_count == 4


def test_solid_hearts_have_two_separate_top_lobes():
    for index, name in sprite_codex.SPRITE_NAMES.items():
        if not name.startswith("HEART_SOLID_"):
            continue

        sprite = sprite_codex.BUILTIN_SPRITES[index]
        row_bytes = (sprite.width + 7) // 8

        for frame in sprite.frames:
            rows = [
                [
                    bool(frame[y * row_bytes + x // 8] & (1 << (7 - x % 8)))
                    for x in range(sprite.width)
                ]
                for y in range(sprite.height)
            ]
            top = next(row for row in rows if any(row))
            center_left = sprite.width // 2 - 1
            center_right = sprite.width // 2

            assert any(top[:center_left])
            assert not top[center_left]
            assert not top[center_right]
            assert any(top[center_right + 1 :])
