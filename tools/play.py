from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.assembler import assemble_text
from src.container import MAX_NTAG216_BYTES, wrap_program, unwrap_program
from src.vm import PixelVM
from run import load_program_sprites, resolve_input_and_output
from src.validator import validate_program


WIDTH = 128
HEIGHT = 64
SCALE = 8
TICK_RATE = 60


def framebuffer_to_surface(fb):
    surface = pygame.Surface((WIDTH, HEIGHT))

    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = (255, 255, 255) if fb.pixels[y][x] else (0, 0, 0)
            surface.set_at((x, y), color)

    return pygame.transform.scale(surface, (WIDTH * SCALE, HEIGHT * SCALE))


def collect_frames(
    input_arg: str,
    max_frames=120,
    max_steps=5000,
    max_size=MAX_NTAG216_BYTES,
):
    input_path, _ = resolve_input_and_output(input_arg)

    source = input_path.read_text(encoding="utf-8")
    code = assemble_text(source, source_name=str(input_path))

    sprites = load_program_sprites(input_path)
    program = wrap_program(code, sprites=sprites, max_size=max_size)

    loaded_code, loaded_sprites = unwrap_program(program)
    
    validate_program(loaded_code, loaded_sprites)

    frames = []
    last_frame_index = None

    def on_frame(fb, ticks):
        nonlocal last_frame_index
        frames.append([fb, max(1, ticks)])
        last_frame_index = len(frames) - 1

    def on_wait(ticks):
        if last_frame_index is not None:
            frames[last_frame_index][1] += ticks

    vm = PixelVM(
        card_sprites=loaded_sprites,
        on_frame=on_frame,
        on_wait=on_wait,
    )
    vm.run(loaded_code, max_frames=max_frames, max_steps=max_steps)

    return input_path, frames


def should_close(event) -> bool:
    return event.type == pygame.QUIT or (
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
    )


def play(
    input_arg: str,
    max_frames=120,
    max_steps=5000,
    max_size=MAX_NTAG216_BYTES,
):
    input_path, frames = collect_frames(
        input_arg,
        max_frames=max_frames,
        max_steps=max_steps,
        max_size=max_size,
    )

    if not frames:
        print("No frames produced. Add SHOW or FRAME instructions.")
        return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
    pygame.display.set_caption(f"Pixel Preview - {input_path.name}")

    surfaces = [framebuffer_to_surface(fb) for fb, _ticks in frames]

    running = True
    index = 0

    while running:
        fb, ticks = frames[index]
        duration = ticks / TICK_RATE

        start = time.time()

        while time.time() - start < duration:
            for event in pygame.event.get():
                if should_close(event):
                    running = False
                    break

            screen.blit(surfaces[index], (0, 0))
            pygame.display.flip()

            if not running:
                break

            time.sleep(0.005)

        index = (index + 1) % len(frames)

    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Play Pixel Console animation preview")
    parser.add_argument("input", help="Program name or path to .pxla file")
    parser.add_argument("--max-frames", type=int, default=120, help="Preview frame limit")
    parser.add_argument("--max-steps", type=int, default=5000, help="VM instruction limit")
    parser.add_argument(
        "--max-size",
        type=int,
        default=MAX_NTAG216_BYTES,
        help="Author-side card capacity limit in bytes",
    )
    args = parser.parse_args()

    play(
        args.input,
        max_frames=args.max_frames,
        max_steps=args.max_steps,
        max_size=args.max_size,
    )


if __name__ == "__main__":
    main()
