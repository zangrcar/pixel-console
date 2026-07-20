# Pixel Assembly Language (PXLA) Specification v0.1

**Status:** Implemented MVP

PXLA (Pixel Assembly Language) is a small assembly language for writing programs that run on the Pixel VM. It is designed to compile into compact bytecode that is stored on NFC cards and executed by the Raspberry Pi interpreter.

---

# General Rules

* One instruction per line.
* Instructions are case-insensitive.
* Labels are case-sensitive (recommended: lowercase).
* Whitespace is ignored except as a separator.
* Blank lines are ignored.

Example:

```asm
clear 0
mode 1

rect 0 0 128 64

frame 60
end
```

---

# Comments

Everything after a comment marker is ignored.

Supported comment markers:

```asm
; this is a comment
// this is also a comment
# this is also a comment
```

Example:

```asm
clear 0      ; clear screen
mode 1       // drawing mode
frame 60     # wait one second
```

Only the first occurring comment marker outside a quoted string is considered.
For example, `text 0 0 "TI SI #1"` preserves the `#` character.

---

# Numbers

Numbers are decimal integers.

Examples:

```asm
0
12
64
127
255
```

Hexadecimal is not currently supported.

---

# Labels

Labels define jump targets.

A label is written as:

```asm
label_name:
```

Example:

```asm
loop:
```

Labels occupy no space in the output bytecode.

Example:

```asm
setv 0 10

loop:
frame 5
djnz 0 loop

end
```

---

# Variables

The VM contains eight variables.

```text
V0
V1
V2
V3
V4
V5
V6
V7
```

In PXLA they are referenced by their numeric index:

```asm
setv 0 10
addv 0 -1
```

---

# Coordinates

Origin:

```text
(0,0)
```

is the upper-left corner.

Coordinate system:

```text
x increases →
y increases ↓
```

Screen size:

```text
Width: 128 pixels
Height: 64 pixels
```

Coordinates outside the screen are clipped by the VM.

---

# Draw Modes

Draw mode affects all drawing instructions.

| Mode | Meaning       |
| ---- | ------------- |
| 0    | Clear pixels  |
| 1    | Set pixels    |
| 2    | XOR pixels    |
| 3    | Invert pixels |

Example:

```asm
mode 1
```

---

# Instructions

The MVP opcode values are stable. Instruction sizes include the opcode byte.

| Opcode | Instruction | Size |
| ------ | ----------- | ---- |
| `0x00` | `END` | 1 |
| `0x01` | `NOP` | 1 |
| `0x02` | `CLEAR` | 2 |
| `0x03` | `MODE` | 2 |
| `0x04` | `SHOW` | 1 |
| `0x05` | `WAIT` | 2 |
| `0x06` | `FRAME` | 2 |
| `0x07` | `JMP` | 3 |
| `0x08` | `SETV` | 3 |
| `0x09` | `ADDV` | 3 |
| `0x0A` | `RANDV` | 3 |
| `0x0B` | `JNZ` | 4 |
| `0x0C` | `JLT` | 5 |
| `0x0D` | `DJNZ` | 4 |
| `0x0E` | `ORIGIN` | 3 |
| `0x0F` | `ORIGINV` | 2 |
| `0x10` | `PSET` | 3 |
| `0x11` | `LINE` | 5 |
| `0x12` | `RECT` | 5 |
| `0x13` | `FRECT` | 5 |
| `0x14` | `INVRECT` | 5 |
| `0x15` | `TEXT` | 4 + stored text bytes |
| `0x16` | `FONT` | 3 |
| `0x17` | `SPR` | 5 |
| `0x18` | `SPRV` | 4 |
| `0x19` | `MOVE` | 3 |

Relative jump offsets are signed 16-bit values measured from the first byte
after the complete jump instruction.

---

## END

Stops execution.

Syntax

```asm
end
```

Example

```asm
end
```

---

## NOP

Does nothing.

Syntax

```asm
nop
```

---

## CLEAR

Fills the entire framebuffer.

Syntax

```asm
clear color
```

Parameters

```
color
0 = black
1 = white
```

Example

```asm
clear 0
```

---

## MODE

Sets the current draw mode.

Syntax

```asm
mode mode
```

Example

```asm
mode 1
```

---

## SHOW

Displays the current framebuffer.

Syntax

```asm
show
```

---

## WAIT

Extends the display time of the current frame without emitting a new frame.

Syntax

```asm
wait ticks
```

Example

```asm
wait 30
```

---

## FRAME

Displays the framebuffer and waits.

Syntax

```asm
frame ticks
```

Example

```asm
frame 60
```

---

## SETV

Sets a variable.

Syntax

```asm
setv variable value
```

Example

```asm
setv 0 100
```

Result

```text
V0 = 100
```

---

## ADDV

Adds a signed integer to a variable.

Syntax

```asm
addv variable delta
```

Example

```asm
addv 0 -4
```

Result

```text
V0 = V0 - 4
```

Values wrap around 0–255.

---

## RANDV

Stores a random integer.

Syntax

```asm
randv variable maximum
```

Example

```asm
randv 0 127
```

Produces

```text
0 ≤ V0 ≤ 127
```

---

## JMP

Unconditional jump.

Syntax

```asm
jmp label
```

Example

```asm
jmp loop
```

---

## JNZ

Jump if variable is not zero.

Syntax

```asm
jnz variable label
```

Example

```asm
jnz 0 loop
```

Equivalent to

```text
if V0 != 0:
    goto loop
```

---

## JLT

Jumps when a variable is less than an unsigned value.

Syntax

```asm
jlt variable value label
```

Example

```asm
jlt 0 10 loop
```

---

## DJNZ

Decrement variable then jump if not zero.

Syntax

```asm
djnz variable label
```

Example

```asm
djnz 2 loop
```

Equivalent to

```text
V2--

if V2 != 0:
    goto loop
```

Variables wrap around 8 bits.

---

## ORIGIN

Sets drawing origin.

Syntax

```asm
origin x y
```

Example

```asm
origin 20 10
```

All subsequent drawing is offset by

```text
(+20,+10)
```

---

## ORIGINV

Sets origin from variables.

Syntax

```asm
originv xVariable yVariable
```

Example

```asm
originv V0,V1
```

Equivalent to

```text
origin(V0,V1)
```

---

## PSET

Draws one pixel.

Syntax

```asm
pset x y
```

Example

```asm
pset 40 20
```

---

## LINE

Draws a clipped line.

Syntax

```asm
line x0 y0 x1 y1
```

Example

```asm
line 0 0 127 63
```

---

## RECT

Draws an outline rectangle.

Syntax

```asm
rect x y width height
```

Example

```asm
rect 0 0 128 64
```

---

## FRECT

Draws a filled rectangle.

Syntax

```asm
frect x y width height
```

Example

```asm
frect 20 10 30 12
```

---

## INVRECT

Inverts a rectangle.

Syntax

```asm
invrect x y width height
```

Example

```asm
invrect 0 0 128 64
```

---

## TEXT

Draws text using the currently selected pixel font and scale.

Syntax

```asm
text x y "string"
```

Example

```asm
text 10 10 "HELLO"
```

Source files are UTF-8. Supported Slovenian characters are stored as one byte:

| Byte | Character |
| ---- | --------- |
| `0x80` | `Č` |
| `0x81` | `Š` |
| `0x82` | `Ž` |
| `0x83` | `č` |
| `0x84` | `š` |
| `0x85` | `ž` |

---

## FONT

Selects a pixel font and integer scale.

Syntax

```asm
font font_id scale
```

Example

```asm
font 0 1
```

`font_id` is `0..4`. Scale is `1..4`; one glyph pixel becomes a square
of `scale` by `scale` display pixels.

---

## SPR

Draws a sprite.

Syntax

```asm
spr x y sprite frame
```

Example

```asm
spr 40 20 0 0
```

---

## SPRV

Draws a sprite using origin variables.

Syntax

```asm
sprv xVariable yVariable sprite frame
```

Example

```asm
sprv 0 1 0 0
```

---

## MOVE

Moves the current drawing origin by signed 8-bit deltas.

Syntax

```asm
move dx dy
```

Example

```asm
move -2 3
```

The old assembler spelling `moveorig` is accepted as a compatibility alias,
but new programs should use `move`.

---

# Complete Example

```asm
clear 0

mode 1

rect 0 0 128 64

setv 0 5

loop:

    frame 20

    addv 0 -1

    djnz 0 loop

end
```

---

# Intentionally Outside the MVP

Hexadecimal and binary literals, constants, macros, include files, string
tables, compression, subroutines, audio and networking are intentionally
omitted to keep the assembler, container and VM small.
