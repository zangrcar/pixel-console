MAGIC = b"PXL1"


def wrap_code(code):
    if len(code) > 888:
        raise ValueError("Program is too large for NTAG216")

    total_len = 4 + 2 + len(code)

    return (
        MAGIC +
        total_len.to_bytes(2, "little") +
        code
    )


def unwrap_code(data):
    if data[:4] != MAGIC:
        raise ValueError("Bad magic")

    total_len = int.from_bytes(data[4:6], "little")

    if total_len > len(data):
        raise ValueError("Truncated container")

    return data[6:total_len]