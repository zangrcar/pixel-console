import random
from src.framebuffer import FrameBuffer


OP_END = 0x00
OP_CLEAR = 0x02
OP_MODE = 0x03
OP_SHOW = 0x04
OP_FRAME = 0x06
OP_SETV = 0x08
OP_ADDV = 0x09
OP_RANDV = 0x0A
OP_DJNZ = 0x0D
OP_ORIGIN = 0x0E
OP_ORIGINV = 0x0F
OP_PSET = 0x10
OP_RECT = 0x12
OP_FRECT = 0x13
OP_TEXT = 0x15


class VMError(Exception):
    pass


class PixelVM:
    def __init__(self):
        self.fb = FrameBuffer()
        self.pc = 0
        self.mode = 1
        self.frame_number = 0
        self.vars = [0]*8
        self.ox = 0
        self.oy = 0

    def read_u8(self, code):
        if self.pc >= len(code):
            raise VMError("Unexpected end of bytecode")
        value = code[self.pc]
        self.pc += 1
        return value
    
    def read_text(self, code, length):
        if self.pc + length >= len(code):
            raise VMError("Unexpected end of bytecode")
        value = bytes(code[self.pc:self.pc+length]).decode("ascii")
        self.pc += length
        return value
        
    
    def read_i8(self, code):
        raw = self.read_u8(code)
        return int.from_bytes(bytes([raw]), signed=True)
    
    def read_i16(self, code):
        lo = self.read_u8(code)
        hi = self.read_u8(code)
        raw = lo | (hi << 8)

        if raw >= 0x8000:
            raw -= 0x10000

        return raw

    def save_frame(self):
        path = f"output/frame_{self.frame_number:04}.png"
        self.fb.save_png(path)
        self.frame_number += 1
        print(f"Saved {path}")

    def run(self, code):
        self.pc = 0

        while True:
            opcode = self.read_u8(code)

            if opcode == OP_END:
                return

            elif opcode == OP_CLEAR:
                color = self.read_u8(code)
                self.fb.clear(color)

            elif opcode == OP_MODE:
                self.mode = self.read_u8(code)

            elif opcode == OP_SHOW:
                self.save_frame()

            elif opcode == OP_FRAME:
                ticks = self.read_u8(code)
                self.save_frame()
                # For laptop testing we ignore real timing for now.
                # Later, ticks can mean 1/60 second units.
                
            elif opcode == OP_SETV:
                var = self.read_u8(code)
                self.vars[var] = self.read_u8(code)
            
            elif opcode == OP_ADDV:
                var = self.read_u8(code)
                delta = self.read_i8(code)
                self.vars[var] = (self.vars[var] + delta) & 0xFF

            elif opcode == OP_RANDV:
                var = self.read_u8(code)
                max = self.read_u8(code)
                
                self.vars[var] = random.randint(1, max)
                
            elif opcode == OP_DJNZ:
                var = self.read_u8(code)
                offset = self.read_i16(code)

                self.vars[var] = (self.vars[var] - 1) & 0xFF

                if self.vars[var] != 0:
                    self.pc += offset
                
            elif opcode == OP_ORIGIN:
                self.ox = self.read_u8(code)
                self.oy = self.read_u8(code)
                
            elif opcode == OP_ORIGINV:
                packed = self.read_u8(code)
                x_var = packed >> 4
                y_var = packed & 0x0F
                self.ox = self.vars[x_var]
                self.oy = self.vars[y_var]
            
            elif opcode == OP_PSET:
                x = self.read_u8(code)
                y = self.read_u8(code)
                self.fb.pset(self.ox + x, self.oy + y, self.mode)

            elif opcode == OP_RECT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                w = self.read_u8(code)
                h = self.read_u8(code)
                self.fb.rect(x, y, w, h, self.mode)

            elif opcode == OP_FRECT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                w = self.read_u8(code)
                h = self.read_u8(code)
                self.fb.frect(x, y, w, h, self.mode)

            elif opcode == OP_TEXT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                length = self.read_u8(code)
                text = self.read_text(code, length)
                self.fb.displayText(x, y, text, self.mode)
                
            else:
                raise VMError(f"Unknown opcode: 0x{opcode:02X}")