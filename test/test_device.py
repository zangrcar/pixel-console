import pytest

from src.assembler import assemble_text
from src.container import ContainerError, wrap_program
from src.device import (
    BOOT_SECONDS,
    ERROR_SECONDS,
    LAST_FRAME_SECONDS,
    STATE_BOOT,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PLAYING,
    STATE_READING,
    make_idle_frame,
    run_console,
)
from src.error_screen import make_error_frame
from src.framebuffer import FrameBuffer, WIDTH
from src.nfc import NFCError
from src.sprite import BUILTIN_SPRITES, SPRITE_IDS
from src.vm import VMError


class FakeDisplay:
    def __init__(self):
        self.events = []
        self.frames = []
        self.blank_calls = 0

    def show(self, framebuffer):
        self.events.append("show")
        self.frames.append(framebuffer.copy())

    def clear(self):
        self.events.append("clear")

    def blank(self):
        self.events.append("blank")
        self.blank_calls += 1


class FakeNFC:
    def __init__(
        self,
        raw_data,
        wait_error=None,
        read_error=None,
        removal_error=None,
        removal_checks=None,
    ):
        self.raw_data = raw_data
        self.wait_error = wait_error
        self.read_error = read_error
        self.removal_error = removal_error
        self.removal_checks = list(removal_checks or [])
        self.events = []
        self.read_calls = 0

    def wait_for_card(self):
        self.events.append("wait_card")
        if self.wait_error is not None:
            raise self.wait_error
        return b"\x01\x02\x03\x04"

    def read_ntag216_user_memory(self):
        self.events.append("read")
        self.read_calls += 1
        if self.read_error is not None:
            raise self.read_error
        return self.raw_data

    def wait_for_removal(self):
        self.events.append("wait_removal")
        self.events.extend(self.removal_checks)
        if self.removal_error is not None:
            raise self.removal_error


def pixels(framebuffer):
    return tuple(tuple(row) for row in framebuffer.pixels)


def test_idle_frame_uses_large_builtin_heart_above_tap_card():
    expected = FrameBuffer()
    heart = BUILTIN_SPRITES[SPRITE_IDS["HEART_SOLID_48"]]
    expected.sprite((WIDTH - heart.width) // 2, 0, heart)
    expected.displayText((WIDTH - (len("TAP CARD") * 6 - 1)) // 2, 53, "TAP CARD")

    assert pixels(make_idle_frame()) == pixels(expected)


def test_success_flow_plays_frames_waits_for_removal_and_returns_idle():
    code = assemble_text(
        "clear 0\n"
        "pset 1 1\n"
        "show\n"
        "wait 3\n"
        "frame 2\n"
        "end\n"
    )
    display = FakeDisplay()
    nfc = FakeNFC(wrap_program(code))
    sleeps = []

    states = run_console(
        display=display,
        nfc=nfc,
        sleep_fn=sleeps.append,
        max_cards=1,
    )

    assert states == [STATE_BOOT, STATE_IDLE, STATE_READING, STATE_PLAYING, STATE_IDLE]
    assert nfc.events == ["wait_card", "read", "wait_removal"]
    assert nfc.read_calls == 1
    assert sleeps == [
        BOOT_SECONDS,
        1 / 60,
        3 / 60,
        2 / 60,
        LAST_FRAME_SECONDS,
    ]
    assert len(display.frames) == 6
    assert display.frames[3].pixels[1][1] == 1
    assert display.frames[4].pixels[1][1] == 1
    assert pixels(display.frames[-1]) == pixels(make_idle_frame())
    assert display.blank_calls == 1


def test_invalid_card_shows_error_then_waits_for_removal_and_returns_idle(capsys):
    display = FakeDisplay()
    nfc = FakeNFC(b"bad")
    sleeps = []

    states = run_console(
        display=display,
        nfc=nfc,
        sleep_fn=sleeps.append,
        max_cards=1,
    )

    assert states == [STATE_BOOT, STATE_IDLE, STATE_READING, STATE_ERROR, STATE_IDLE]
    assert nfc.events == ["wait_card", "read", "wait_removal"]
    assert pixels(display.frames[-2]) == pixels(
        make_error_frame(ContainerError("Container too short"))
    )
    assert sleeps == [BOOT_SECONDS, ERROR_SECONDS]
    assert "Container too short" in capsys.readouterr().err


def test_execution_limit_uses_error_state_and_err_05_screen():
    code = assemble_text("loop:\nnop\njmp loop\n")
    display = FakeDisplay()
    nfc = FakeNFC(wrap_program(code))

    states = run_console(
        display=display,
        nfc=nfc,
        sleep_fn=lambda _seconds: None,
        max_cards=1,
        max_steps=5,
    )

    assert states == [STATE_BOOT, STATE_IDLE, STATE_READING, STATE_PLAYING, STATE_ERROR, STATE_IDLE]
    assert pixels(display.frames[-2]) == pixels(
        make_error_frame(VMError("Execution limit exceeded"))
    )


def test_card_that_stays_on_reader_is_not_started_again():
    display = FakeDisplay()
    nfc = FakeNFC(
        wrap_program(assemble_text("show\nend\n")),
        removal_checks=["still_present", "still_present", "removed"],
    )

    states = run_console(
        display=display,
        nfc=nfc,
        sleep_fn=lambda _seconds: None,
        max_cards=1,
    )

    assert states.count(STATE_PLAYING) == 1
    assert nfc.read_calls == 1
    assert nfc.events == [
        "wait_card",
        "read",
        "wait_removal",
        "still_present",
        "still_present",
        "removed",
    ]


def test_removal_failure_gets_controlled_error_screen_and_returns_idle():
    display = FakeDisplay()
    nfc = FakeNFC(
        wrap_program(assemble_text("show\nend\n")),
        removal_error=NFCError("Failed checking NFC card removal"),
    )

    states = run_console(
        display=display,
        nfc=nfc,
        sleep_fn=lambda _seconds: None,
        max_cards=1,
    )

    assert states == [
        STATE_BOOT,
        STATE_IDLE,
        STATE_READING,
        STATE_PLAYING,
        STATE_ERROR,
        STATE_IDLE,
    ]
    assert pixels(display.frames[-2]) == pixels(
        make_error_frame(NFCError("Failed checking NFC card removal"))
    )


def test_keyboard_interrupt_always_blanks_display():
    display = FakeDisplay()
    nfc = FakeNFC(b"", wait_error=KeyboardInterrupt())

    with pytest.raises(KeyboardInterrupt):
        run_console(
            display=display,
            nfc=nfc,
            sleep_fn=lambda _seconds: None,
        )

    assert display.blank_calls == 1
    assert display.events[-1] == "blank"
