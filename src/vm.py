import random
from src.font import FONTS, is_text_byte_supported
from src.framebuffer import FrameBuffer
from src.sprite import BUILTIN_SPRITES


OP_END = 0x00
OP_NOP = 0x01
OP_CLEAR = 0x02
OP_MODE = 0x03
OP_SHOW = 0x04
OP_WAIT = 0x05
OP_FRAME = 0x06
OP_JMP = 0x07
OP_SETV = 0x08
OP_ADDV = 0x09
OP_RANDV = 0x0A
OP_JNZ = 0x0B
OP_JLT = 0x0C
OP_DJNZ = 0x0D
OP_ORIGIN = 0x0E
OP_ORIGINV = 0x0F
OP_PSET = 0x10
OP_LINE = 0x11
OP_RECT = 0x12
OP_FRECT = 0x13
OP_INVRECT = 0x14
OP_TEXT = 0x15
OP_FONT = 0x16
OP_SPR = 0x17
OP_SPRV = 0x18
OP_MOVE = 0x19

class VMError(Exception):
    pass


class PixelVM:
    def __init__(self, card_sprites=None, on_frame=None, on_wait=None):
        self.builtin_sprites = BUILTIN_SPRITES
        self.card_sprites = card_sprites or []
        self.on_frame = on_frame
        self.on_wait = on_wait
        self.reset()

    def reset(self):
        self.fb = FrameBuffer()
        self.pc = 0
        self.mode = 1
        self.frame_number = 0
        self.vars = [0] * 8
        self.ox = 0
        self.oy = 0
        self.font_id = 0
        self.font_scale = 1

    def read_u8(self, code):
        if self.pc >= len(code):
            raise VMError("Unexpected end of bytecode")
        value = code[self.pc]
        self.pc += 1
        return value
    
    def read_text(self, code, length):
        if self.pc + length > len(code):
            raise VMError("Unexpected end of bytecode")
        value = bytes(code[self.pc:self.pc+length])
        self.pc += length

        if not all(is_text_byte_supported(byte) for byte in value):
            raise VMError("Text contains an unsupported byte")

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

    def read_var(self, code):
        var = self.read_u8(code)

        if not 0 <= var <= 7:
            raise VMError(f"Invalid variable index: {var}")

        return var

    def read_varpair(self, code):
        packed = self.read_u8(code)
        x_var = packed >> 4
        y_var = packed & 0x0F

        if not 0 <= x_var <= 7:
            raise VMError(f"Invalid x variable in varpair: {x_var}")

        if not 0 <= y_var <= 7:
            raise VMError(f"Invalid y variable in varpair: {y_var}")

        return x_var, y_var

    def jump_relative(self, code, offset):
        target = self.pc + offset

        if not 0 <= target < len(code):
            raise VMError(f"Invalid jump target: {target}")

        self.pc = target
        
    def emit_frame(self, ticks=1, max_frames=None):
        if self.on_frame is not None:
            self.on_frame(self.fb.copy(), ticks)
        else:
            path = f"output/frame_{self.frame_number:04}.png"
            self.fb.save_png(path)
            print(f"Saved {path}")

        self.frame_number += 1


    def emit_wait(self, ticks):
        if self.on_wait is not None:
            self.on_wait(ticks)
        
    def get_sprite(self, sprite_id, frame=None):
        if sprite_id < 128:
            if sprite_id >= len(self.builtin_sprites):
                raise VMError(f"Invalid built-in sprite id: {sprite_id}")
            sprite = self.builtin_sprites[sprite_id]
        else:
            card_index = sprite_id - 128

            if card_index >= len(self.card_sprites):
                raise VMError(f"Invalid card sprite id: {sprite_id}")

            sprite = self.card_sprites[card_index]

        if frame is not None and not 0 <= frame < sprite.frame_count:
            raise VMError(f"Invalid frame {frame} for sprite {sprite_id}")

        return sprite

    def run(self, code, max_frames=None, max_steps=50000):
        self.reset()

        try:
            code = bytes(code)
        except (TypeError, ValueError) as error:
            raise VMError(f"Invalid bytecode data: {error}") from error

        from src.validator import ValidationError, validate_program

        try:
            validate_program(code, self.card_sprites)
        except ValidationError as error:
            raise VMError(f"Invalid bytecode: {error}") from error

        try:
            return self._execute(code, max_frames=max_frames, max_steps=max_steps)
        except VMError:
            raise
        except (IndexError, UnicodeError) as error:
            raise VMError(f"VM execution failed: {error}") from error

    def _execute(self, code, max_frames=None, max_steps=50000):
        steps = 0

        while True:
            if steps >= max_steps:
                raise VMError("Execution limit exceeded")

            steps += 1
        
            opcode = self.read_u8(code)

            if opcode == OP_END:
                return
            
            if opcode == OP_NOP:
                pass

            elif opcode == OP_CLEAR:
                color = self.read_u8(code)
                self.fb.clear(color)

            elif opcode == OP_MODE:
                self.mode = self.read_u8(code)
                if self.mode > 3:
                    raise VMError(f"Invalid draw mode: {self.mode}")

            elif opcode == OP_SHOW:
                self.emit_frame(1, max_frames)
                if max_frames is not None and self.frame_number >= max_frames:
                    return
            
            elif opcode == OP_WAIT:
                ticks = self.read_u8(code)
                self.emit_wait(ticks)

            elif opcode == OP_FRAME:
                ticks = self.read_u8(code)
                self.emit_frame(ticks, max_frames)
                
                if max_frames is not None and self.frame_number >= max_frames:
                    return
                
            elif opcode == OP_JMP:
                offset = self.read_i16(code)
                self.jump_relative(code, offset)
                
            elif opcode == OP_SETV:
                var = self.read_var(code)
                self.vars[var] = self.read_u8(code)
            
            elif opcode == OP_ADDV:
                var = self.read_var(code)
                delta = self.read_i8(code)
                self.vars[var] = (self.vars[var] + delta) & 0xFF

            elif opcode == OP_RANDV:
                var = self.read_var(code)
                max = self.read_u8(code)
                
                self.vars[var] = random.randint(0, max)
                
            elif opcode == OP_JNZ:
                var = self.read_var(code)
                offset = self.read_i16(code)
                
                if self.vars[var] != 0:
                    self.jump_relative(code, offset)
                    
            elif opcode == OP_JLT:
                var = self.read_var(code)
                val = self.read_u8(code)
                offset = self.read_i16(code)
                
                if self.vars[var] < val:
                    self.jump_relative(code, offset)
                
            elif opcode == OP_DJNZ:
                var = self.read_var(code)
                offset = self.read_i16(code)

                self.vars[var] = (self.vars[var] - 1) & 0xFF

                if self.vars[var] != 0:
                    self.jump_relative(code, offset)
                
            elif opcode == OP_ORIGIN:
                self.ox = self.read_u8(code)
                self.oy = self.read_u8(code)
                
            elif opcode == OP_ORIGINV:
                x_var, y_var = self.read_varpair(code)
                self.ox = self.vars[x_var]
                self.oy = self.vars[y_var]
            
            elif opcode == OP_PSET:
                x = self.read_u8(code)
                y = self.read_u8(code)
                self.fb.pset(self.ox + x, self.oy + y, self.mode)
                
            elif opcode == OP_LINE:
                x0 = self.read_u8(code)
                y0 = self.read_u8(code)
                x1 = self.read_u8(code)
                y1 = self.read_u8(code)
                self.fb.line(
                    self.ox + x0, 
                    self.oy + y0, 
                    self.ox + x1, 
                    self.oy + y1, 
                    self.mode
                )

            elif opcode == OP_RECT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                w = self.read_u8(code)
                h = self.read_u8(code)
                self.fb.rect(self.ox + x, self.oy + y, w, h, self.mode)

            elif opcode == OP_FRECT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                w = self.read_u8(code)
                h = self.read_u8(code)
                self.fb.frect(self.ox + x, self.oy + y, w, h, self.mode)
                
            elif opcode == OP_INVRECT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                w = self.read_u8(code)
                h = self.read_u8(code)
                self.fb.frect(self.ox + x, self.oy + y, w, h, 3)

            elif opcode == OP_TEXT:
                x = self.read_u8(code)
                y = self.read_u8(code)
                length = self.read_u8(code)
                text = self.read_text(code, length)
                self.fb.displayText(
                    self.ox + x,
                    self.oy + y,
                    text,
                    self.mode,
                    self.font_id,
                    self.font_scale,
                )
                
            elif opcode == OP_FONT:
                font_id = self.read_u8(code)
                scale = self.read_u8(code)

                if font_id not in FONTS:
                    raise VMError(f"Invalid font id: {font_id}")

                if not 1 <= scale <= 4:
                    raise VMError(f"Invalid font scale: {scale}")

                self.font_id = font_id
                self.font_scale = scale
            
            elif opcode == OP_SPR:
                x = self.read_u8(code)
                y = self.read_u8(code)
                sprite_id = self.read_u8(code)
                frame = self.read_u8(code)

                sprite = self.get_sprite(sprite_id, frame)

                self.fb.sprite(
                    self.ox + x,
                    self.oy + y,
                    sprite,
                    frame,
                    self.mode
                )
            
            elif opcode == OP_SPRV:
                x_var, y_var = self.read_varpair(code)
                sprite_id = self.read_u8(code)
                frame = self.read_u8(code)

                sprite = self.get_sprite(sprite_id, frame)

                self.fb.sprite(
                    self.vars[x_var],
                    self.vars[y_var],
                    sprite,
                    frame,
                    self.mode
                )
            
            elif opcode == OP_MOVE:
                dx = self.read_i8(code)
                dy = self.read_i8(code)
                
                self.ox = (self.ox + dx) & 0xFF
                self.oy = (self.oy + dy) & 0xFF
            
            else:
                raise VMError(f"Unknown opcode: 0x{opcode:02X}")
