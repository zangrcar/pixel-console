from __future__ import annotations

import time

from src.container import unwrap_program
from src.display import Display
from src.error_screen import show_error
from src.nfc import NFCReader
from src.validator import validate_program
from src.vm import PixelVM


def run_card(display: Display, raw_data: bytes) -> None:
    code, sprites = unwrap_program(raw_data)
    validate_program(code, sprites)

    def on_frame(fb, ticks=1):
        display.show(fb)
        time.sleep(max(1, ticks) / 60)

    def on_wait(ticks):
        time.sleep(max(1, ticks) / 60)

    vm = PixelVM(
        card_sprites=sprites,
        on_frame=on_frame,
        on_wait=on_wait,
    )

    vm.run(
        code,
        max_frames=600,
        max_steps=50000,
    )


def main() -> None:
    display = Display()
    nfc = NFCReader()

    display.clear()

    while True:
        try:
            nfc.wait_for_card()
            raw_data = nfc.read_ntag216_user_memory()
            run_card(display, raw_data)

        except Exception as e:
            show_error(display, "ERR CARD", str(e))
            time.sleep(3)

        finally:
            display.clear()
            time.sleep(0.5)


if __name__ == "__main__":
    main()