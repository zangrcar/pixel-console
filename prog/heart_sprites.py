from src.sprite import Sprite

HEART = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        bytes([
            0b01100110,
            0b11111111,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
            0b00000000,
        ]),
        bytes([
            0b00100100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
            0b00000000,
        ]),
    ]
)


SPRITES = [HEART]