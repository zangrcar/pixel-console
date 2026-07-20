from src import sprite


EXPECTED_SPRITE_NAMES = tuple(
    [f"PIXEL_CAT_{index:02}" for index in range(66)]
    + [
        "HEART_SOLID_08",
        "HEART_SOLID_10",
        "HEART_SOLID_12",
        "HEART_SOLID_14",
        "HEART_SOLID_16",
        "HEART_SOLID_18",
        "HEART_SOLID_20",
        "HEART_SOLID_24",
        "HEART_SOLID_28",
        "HEART_SOLID_32",
        "HEART_SOLID_40",
        "HEART_SOLID_48",
        "HEART_SOLID_56",
        "HEART_SOLID_64",
        "HEART_OUTLINE_16",
        "HEART_OUTLINE_20",
        "HEART_OUTLINE_24",
        "HEART_OUTLINE_28",
        "HEART_OUTLINE_32",
        "HEART_OUTLINE_40",
        "HEART_OUTLINE_48",
        "HEART_OUTLINE_56",
        "HEART_OUTLINE_64",
        "HEART_SPARKLE_16",
        "HEART_SPARKLE_20",
        "HEART_SPARKLE_24",
        "HEART_SPARKLE_28",
        "HEART_SPARKLE_32",
        "HEART_SPARKLE_40",
        "HEART_SPARKLE_48",
        "HEART_SPARKLE_64",
        "DOUBLE_HEART_24",
        "DOUBLE_HEART_28",
        "DOUBLE_HEART_32",
        "DOUBLE_HEART_40",
        "DOUBLE_HEART_48",
        "CONFETTI_BURST_16",
        "CONFETTI_BURST_24",
        "STAR_SINGLE_32",
        "STAR_CLUSTER_48",
        "NESTED_HEART_32",
        "NESTED_HEART_48",
        "NESTED_HEART_64",
        "LOVE_BANNER_96X24",
        "FOREVER_BANNER_112X24",
        "TOGETHER_BANNER_128X24",
        "HAPPY_BANNER_96X24",
        "I_LOVE_YOU_BANNER_128X24",
        "MISS_YOU_BANNER_128X24",
        "HEART_TEXT_BANNER_128X24",
        "RIBBON_TEXT_BANNER_128X24",
        "SPARKLE_TEXT_BANNER_128X24",
        "NESTED_HEART_40",
        "GIFT_32",
        "ROSE_BOUQUET_32",
        "RING_BOX_32",
        "ENVELOPE_HEART_32",
        "FIREWORK_HEART_40",
        "BG_HEART_BORDER_128X64",
        "BG_STAR_BORDER_128X64",
        "BG_RIBBON_BORDER_128X64",
        "BG_CONFETTI_FULL_128X64",
    ]
)


def test_builtin_sprite_ids_and_names_are_stable():
    assert len(sprite.BUILTIN_SPRITES) == 128
    assert set(sprite.SPRITE_NAMES) == set(range(128))

    names = tuple(sprite.SPRITE_NAMES[index] for index in range(128))

    assert names == EXPECTED_SPRITE_NAMES
    assert len(names) == len(set(names))


def test_sprite_name_id_and_object_collections_are_aligned():
    for sprite_id, name in sprite.SPRITE_NAMES.items():
        assert sprite.SPRITE_IDS[name] == sprite_id
        assert sprite.BUILTIN_SPRITES[sprite_id] is getattr(sprite, name)

    canonical_names = set(sprite.SPRITE_NAMES.values())
    aliases = set(sprite.SPRITE_IDS) - canonical_names

    assert aliases
    assert all(0 <= sprite.SPRITE_IDS[name] <= 127 for name in aliases)


def test_builtin_sprite_frame_metadata_and_lengths_are_valid():
    for current_sprite in sprite.BUILTIN_SPRITES:
        assert current_sprite.width > 0
        assert current_sprite.height > 0
        assert current_sprite.frame_count == len(current_sprite.frames)
        assert current_sprite.frame_count > 0

        expected_length = ((current_sprite.width + 7) // 8) * current_sprite.height

        assert all(isinstance(frame, bytes) for frame in current_sprite.frames)
        assert all(len(frame) == expected_length for frame in current_sprite.frames)


def test_dynamic_text_banners_have_common_92_by_14_clear_area():
    names = (
        "HEART_TEXT_BANNER_128X24",
        "RIBBON_TEXT_BANNER_128X24",
        "SPARKLE_TEXT_BANNER_128X24",
    )

    for name in names:
        current_sprite = sprite.BUILTIN_SPRITES[sprite.SPRITE_IDS[name]]
        bytes_per_row = (current_sprite.width + 7) // 8

        for frame in current_sprite.frames:
            for y in range(5, 19):
                for x in range(18, 110):
                    byte = frame[y * bytes_per_row + x // 8]
                    assert not byte & (1 << (7 - x % 8))
