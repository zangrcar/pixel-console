from __future__ import annotations

import signal
import time
import traceback

from src.container import unwrap_program
from src.display import Display
from src.error_screen import show_error
from src.framebuffer import FrameBuffer, WIDTH
from src.nfc import NFCReader
from src.sprite import BUILTIN_SPRITES, SPRITE_IDS
from src.validator import validate_program
from src.vm import PixelVM


STATE_BOOT = "boot"
STATE_IDLE = "idle"
STATE_READING = "reading"
STATE_PLAYING = "playing"
STATE_ERROR = "error"

BOOT_SECONDS = 2.0
ERROR_SECONDS = 5.0
LAST_FRAME_SECONDS = 1.0
TICKS_PER_SECOND = 60
MAX_FRAMES = 1000
MAX_STEPS = 100000


def _text_x(text: str) -> int:
    width = len(text) * 6 - 1
    return max(0, (WIDTH - width) // 2)


def make_boot_frame() -> FrameBuffer:
    fb = FrameBuffer()
    fb.displayText(_text_x("PIXEL CONSOLE"), 12, "PIXEL CONSOLE")

    heart = BUILTIN_SPRITES[SPRITE_IDS["HEART_SOLID_16"]]
    fb.sprite((WIDTH - heart.width) // 2, 34, heart)

    return fb


def make_idle_frame() -> FrameBuffer:
    fb = FrameBuffer()
    heart = BUILTIN_SPRITES[SPRITE_IDS["HEART_SOLID_48"]]
    fb.sprite((WIDTH - heart.width) // 2, 0, heart)
    fb.displayText(_text_x("TAP CARD"), 53, "TAP CARD")
    return fb


def make_reading_frame() -> FrameBuffer:
    fb = FrameBuffer()
    fb.displayText(_text_x("READING..."), 28, "READING...")
    return fb


def load_card(raw_data: bytes):
    code, sprites = unwrap_program(raw_data)
    validate_program(code, sprites)
    return code, sprites


def run_program(
    display,
    code: bytes,
    sprites,
    sleep_fn=time.sleep,
    max_frames=MAX_FRAMES,
    max_steps=MAX_STEPS,
) -> int:
    emitted_frames = 0

    def on_frame(fb, ticks=1):
        nonlocal emitted_frames
        display.show(fb)
        emitted_frames += 1
        sleep_fn(max(1, ticks) / TICKS_PER_SECOND)

    def on_wait(ticks):
        sleep_fn(max(1, ticks) / TICKS_PER_SECOND)

    vm = PixelVM(
        card_sprites=sprites,
        on_frame=on_frame,
        on_wait=on_wait,
    )
    vm.run(code, max_frames=max_frames, max_steps=max_steps)

    return emitted_frames


def run_card(
    display,
    raw_data: bytes,
    sleep_fn=time.sleep,
    max_frames=MAX_FRAMES,
    max_steps=MAX_STEPS,
) -> int:
    code, sprites = load_card(raw_data)
    return run_program(
        display,
        code,
        sprites,
        sleep_fn=sleep_fn,
        max_frames=max_frames,
        max_steps=max_steps,
    )


def run_console(
    display=None,
    nfc=None,
    sleep_fn=time.sleep,
    max_cards=None,
    max_frames=MAX_FRAMES,
    max_steps=MAX_STEPS,
):
    # State history is only retained by bounded fake-backend test runs.
    states = [] if max_cards is not None else None
    display_backend = display

    def set_state(state):
        if states is not None:
            states.append(state)

    try:
        set_state(STATE_BOOT)
        display_backend = display_backend or Display()
        display_backend.show(make_boot_frame())
        sleep_fn(BOOT_SECONDS)

        try:
            nfc_backend = nfc or NFCReader()
        except Exception as error:
            traceback.print_exc()
            set_state(STATE_ERROR)
            show_error(display_backend, error)
            sleep_fn(ERROR_SECONDS)
            raise

        processed_cards = 0

        while True:
            set_state(STATE_IDLE)
            display_backend.show(make_idle_frame())
            card_detected = False

            try:
                nfc_backend.wait_for_card()
                card_detected = True

                set_state(STATE_READING)
                display_backend.show(make_reading_frame())
                raw_data = nfc_backend.read_ntag216_user_memory()
                code, sprites = load_card(raw_data)

                set_state(STATE_PLAYING)
                emitted_frames = run_program(
                    display_backend,
                    code,
                    sprites,
                    sleep_fn=sleep_fn,
                    max_frames=max_frames,
                    max_steps=max_steps,
                )

                if emitted_frames:
                    sleep_fn(LAST_FRAME_SECONDS)

            except KeyboardInterrupt:
                raise
            except Exception as error:
                traceback.print_exc()
                set_state(STATE_ERROR)
                show_error(display_backend, error)
                sleep_fn(ERROR_SECONDS)

            if card_detected:
                try:
                    nfc_backend.wait_for_removal()
                except KeyboardInterrupt:
                    raise
                except Exception as error:
                    traceback.print_exc()
                    set_state(STATE_ERROR)
                    show_error(display_backend, error)
                    sleep_fn(ERROR_SECONDS)

                processed_cards += 1

            if max_cards is not None and processed_cards >= max_cards:
                set_state(STATE_IDLE)
                display_backend.show(make_idle_frame())
                break

        return states or []

    finally:
        if display_backend is not None:
            try:
                display_backend.blank()
            except Exception:
                traceback.print_exc()


def _handle_shutdown(_signum, _frame) -> None:
    raise KeyboardInterrupt


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_shutdown)

    try:
        run_console()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
