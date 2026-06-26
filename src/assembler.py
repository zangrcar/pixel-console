from pathlib import Path

OPCODES = {
    "end": 0x00,
    "nop": 0x01,
    "clear": 0x02,
    "mode": 0x03,
    "show": 0x04,
    "wait": 0x05,
    "frame": 0x06,
    "jmp": 0x07,
    "setv": 0x08,
    "addv": 0x09,
    "randv": 0x0A,
    "jnz": 0x0B,
    "jlt": 0x0C,
    "djnz": 0x0D,
    "origin": 0x0E,
    "originv": 0x0F,
    "pset": 0x10,
    "line": 0x11,
    "rect": 0x12,
    "frect": 0x13,
    "invrect": 0x14,
    "text": 0x15,
    "font": 0x16,
    "spr": 0x17,
    "sprv": 0x18,
}

FORMATS = {
    "end": [],
    "nop": [],
    "clear": ["u8"],
    "mode": ["u8"],
    "show": [],
    "wait": ["u8"],
    "frame": ["u8"],
    "jmp": ["rel16"],
    "setv": ["var", "u8"],
    "addv": ["var", "i8"],
    "randv": ["var", "u8"],
    "jnz": ["var", "rel16"],
    "jlt": ["var", "u8", "rel16"],
    "djnz": ["var", "rel16"],
    "origin": ["u8", "u8"],
    "originv": ["varpair"],
    "pset": ["u8", "u8"],
    "line": ["u8", "u8", "u8", "u8"],
    "rect": ["u8", "u8", "u8", "u8"],
    "frect": ["u8", "u8", "u8", "u8"],
    "invrect": ["u8", "u8", "u8", "u8"],
    "text": ["u8", "u8", "string"],
    "font": ["u8"],
    "spr": ["u8", "u8", "u8", "u8"],
    "sprv": ["varpair", "u8", "u8"],
}


def remove_comment(line):
    cut = len(line)

    for marker in (";", "//", "#"):
        index = line.find(marker)
        if index != -1:
            cut = min(cut, index)

    return line[:cut].strip()


def parse_line(line):
    line = remove_comment(line)

    if not line:
        return None

    if line.endswith(":"):
        return ("label", line[:-1], [])

    parts = line.split(maxsplit=1)
    mnemonic = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    if mnemonic == "text":
        args = parse_text_args(rest)
    else:
        args = rest.split() if rest else []

    return ("instruction", mnemonic, args)


def parse_text_args(rest):
    # syntax: text x y "hello world"
    first = rest.split(maxsplit=2)

    if len(first) != 3:
        raise ValueError("text expects: text x y \"string\"")

    x, y, string_part = first

    if not (string_part.startswith('"') and string_part.endswith('"')):
        raise ValueError("text string must be quoted")

    text = string_part[1:-1]

    return [x, y, text]


def instruction_size(mnemonic, args):
    size = 1  # opcode

    for kind, arg in zip(FORMATS[mnemonic], args):
        if kind in ("u8", "i8", "var", "varpair"):
            size += 1
        elif kind == "rel16":
            size += 2
        elif kind == "string":
            size += 1 + len(arg.encode("ascii"))
        else:
            raise ValueError(f"Unknown argument kind: {kind}")

    return size


def emit_u8(value):
    value = int(value)

    if not (0 <= value <= 255):
        raise ValueError(f"u8 out of range: {value}")

    return [value]


def emit_i8(value):
    value = int(value)

    if not (-128 <= value <= 127):
        raise ValueError(f"i8 out of range: {value}")

    if value < 0:
        value += 0x100

    return [value]


def emit_var(value):
    value = int(value)

    if not (0 <= value <= 7):
        raise ValueError(f"variable must be 0..7, got {value}")

    return [value]


def emit_varpair(value):
    # Accepts either "0,1" or "V0,V1"
    value = value.replace("V", "").replace("v", "")
    parts = value.split(",")

    if len(parts) != 2:
        raise ValueError("varpair must look like 0,1 or V0,V1")

    x_var = int(parts[0])
    y_var = int(parts[1])

    if not (0 <= x_var <= 7 and 0 <= y_var <= 7):
        raise ValueError("varpair variables must be 0..7")

    return [(x_var << 4) | y_var]


def emit_i16(value):
    if not (-32768 <= value <= 32767):
        raise ValueError(f"rel16 out of range: {value}")

    if value < 0:
        value += 0x10000

    return [value & 0xFF, (value >> 8) & 0xFF]


def emit_string(value):
    data = value.encode("ascii")

    if len(data) > 64:
        raise ValueError("text too long, max 64 bytes")

    return [len(data), *data]


def collect_labels(parsed_lines):
    labels = {}
    pc = 0

    for kind, name, args in parsed_lines:
        if kind == "label":
            if not name:
                raise ValueError("empty label")

            if name in labels:
                raise ValueError(f"duplicate label: {name}")

            labels[name] = pc
            continue

        if name not in OPCODES:
            raise ValueError(f"unknown instruction: {name}")

        expected = len(FORMATS[name])
        actual = len(args)

        if expected != actual:
            raise ValueError(f"{name} expects {expected} args, got {actual}")

        pc += instruction_size(name, args)

    return labels


def emit_arg(kind, arg, labels, pc_after_instruction):
    if kind == "u8":
        return emit_u8(arg)

    if kind == "i8":
        return emit_i8(arg)

    if kind == "var":
        return emit_var(arg)

    if kind == "varpair":
        return emit_varpair(arg)

    if kind == "string":
        return emit_string(arg)

    if kind == "rel16":
        if arg not in labels:
            raise ValueError(f"unknown label: {arg}")

        offset = labels[arg] - pc_after_instruction
        return emit_i16(offset)

    raise ValueError(f"unknown argument kind: {kind}")


def assemble_instruction(mnemonic, args, labels, pc):
    if mnemonic not in OPCODES:
        raise ValueError(f"unknown instruction: {mnemonic}")

    fmt = FORMATS[mnemonic]

    if len(args) != len(fmt):
        raise ValueError(f"{mnemonic} expects {len(fmt)} args, got {len(args)}")

    size = instruction_size(mnemonic, args)
    pc_after_instruction = pc + size

    output = [OPCODES[mnemonic]]

    for kind, arg in zip(fmt, args):
        output.extend(emit_arg(kind, arg, labels, pc_after_instruction))

    return output


def assemble_text(text):
    parsed_lines = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        try:
            parsed = parse_line(line)
            if parsed is not None:
                parsed_lines.append(parsed)
        except Exception as e:
            raise ValueError(f"Line {line_number}: {e}")

    labels = collect_labels(parsed_lines)

    output = []
    pc = 0

    for kind, mnemonic, args in parsed_lines:
        if kind == "label":
            continue

        assembled = assemble_instruction(mnemonic, args, labels, pc)
        output.extend(assembled)
        pc += len(assembled)

    return bytes(output)

def assemble_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    bytecode = assemble_text(source)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as f:
        f.write(bytecode)

    print(f"Wrote {len(bytecode)} bytes to {output_path}")