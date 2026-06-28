from src.container import unwrap_program

def inspect_bytes(data):
    print(f"Total size: {len(data)} bytes")
    print(f"Fits NTAG216: {'yes' if len(data) <= 888 else 'no'}")
    print(f"Remaining: {888 - len(data)} bytes")

    try:
        code, sprites = unwrap_program(data)

        print()
        print("PXL1 container: yes")
        print(f"Sprites: {len(sprites)}")
        print(f"Code size: {len(code)} bytes")

        for i, sprite in enumerate(sprites):
            print(
                f"  Sprite {i}: "
                f"{sprite.width}x{sprite.height}, "
                f"{sprite.frame_count} frame(s)"
            )

    except Exception as e:
        print()
        print("PXL1 container: no")
        print(f"Reason: {e}")

    print()
    print("Hex:")
    print(data.hex(" "))