# Pixel Assembly Language (PXLA) Specification v0.1

**Status:** Draft (MVP)

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

Only the first occurring comment marker on a line is considered.

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
originv 0 1
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

Draws ASCII text.

Syntax

```asm
text x y "string"
```

Example

```asm
text 10 10 "HELLO"
```

Current implementation may temporarily use simplified syntax until string parsing is added.

---

## FONT

Selects a font.

Syntax

```asm
font id
```

Example

```asm
font 0
```

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

# Future Features

Planned additions include:

* Hexadecimal literals
* Binary literals
* Constants
* Macros
* Include files
* Multiple fonts
* Sprite banks
* String tables
* Compiler warnings
* Better diagnostics

These features are intentionally omitted from the MVP to keep both the assembler and the VM small and easy to understand.
