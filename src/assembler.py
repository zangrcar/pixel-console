OPCODES = {
    "end": 0x00,
    "clear": 0x02,
    "mode": 0x03,
    "show": 0x04,
    "frame": 0x06,
    "setv": 0x08,
    "addv": 0x09,
    "randv": 0x0A,
    "djnz": 0x0D,
    "origin": 0x0E,
    "originv": 0x0F,
    "pset": 0x10,
    "rect": 0x12,
    "frect": 0x13,   
}


ARG_COUNTS = {
    "end": 0,
    "clear": 1,
    "mode": 1,
    "show": 0,
    "frame": 1,
    "setv": 2,
    "addv": 2,
    "randv": 2,
    "djnz": 3,
    "origin": 2,
    "originv": 1,
    "pset": 2,
    "rect": 4,
    "frect": 4,
}

COMMENT_MARKERS = [";", "//", "#"]

def remove_comment(line):
    first_comment_pos = len(line)

    for marker in COMMENT_MARKERS:
        pos = line.find(marker)
        if pos != -1:
            first_comment_pos = min(first_comment_pos, pos)

    return line[:first_comment_pos].strip()

def assemble_line(line):
    line = remove_comment(line)

    if not line:
        return []

    parts = line.split()
    mnemonic = parts[0].lower()
    args = parts[1:]

    if mnemonic not in OPCODES:
        raise ValueError(f"Unknown instruction: {mnemonic}")

    expected = ARG_COUNTS[mnemonic]

    if len(args) != expected:
        raise ValueError(
            f"{mnemonic} expects {expected} args, got {len(args)}"
        )

    output = [OPCODES[mnemonic]]

    for arg in args:
        value = int(arg)
        if not (0 <= value <= 255):
            raise ValueError(f"Argument out of byte range: {value}")
        output.append(value)

    return output


def assemble_text(text):
    output = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        try:
            output.extend(assemble_line(line))
        except Exception as e:
            raise ValueError(f"Line {line_number}: {e}")

    return bytes(output)


def assemble_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    bytecode = assemble_text(source)

    with open(output_path, "wb") as f:
        f.write(bytecode)

    print(f"Wrote {len(bytecode)} bytes to {output_path}")