def inspect_bytes(data):
    print(f"Total size: {len(data)} bytes")
    print(f"Fits NTAG216: {'yes' if len(data) <= 888 else 'no'}")
    print(f"Remaining: {888 - len(data)} bytes")
    print("Hex:")
    print(data.hex(" "))