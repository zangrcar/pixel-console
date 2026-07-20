import pytest

from src.assembler import AssemblerError
from src.container import CRCError, ContainerError, UnsupportedVersionError
from src.error_screen import ERRORS, classify_error, make_error_frame, show_error
from src.nfc import NFCError
from src.validator import ValidationError
from src.vm import VMError


class HardwareError(Exception):
    pass


@pytest.mark.parametrize(
    "error, code",
    [
        (ContainerError("Bad magic"), "ERR 01"),
        (CRCError("Bad CRC"), "ERR 02"),
        (UnsupportedVersionError("Unsupported"), "ERR 03"),
        (ValidationError("Invalid bytecode"), "ERR 04"),
        (VMError("Execution limit exceeded"), "ERR 05"),
        (VMError("Invalid asset"), "ERR 06"),
        (HardwareError("Generic hardware failure"), "ERR 07"),
        (ContainerError("Truncated container"), "ERR 08"),
        (ContainerError("Bad total length"), "ERR 08"),
        (ContainerError("Input exceeds NTAG216 capacity"), "ERR 08"),
        (ContainerError("Truncated sprite header"), "ERR 09"),
        (ContainerError("Only raw sprite encoding is supported"), "ERR 09"),
        (ContainerError("Bad sprite data length"), "ERR 09"),
        (ContainerError("Empty code section"), "ERR 10"),
        (ValidationError("Empty program"), "ERR 10"),
        (ValidationError("Unknown opcode: 0xFF"), "ERR 11"),
        (VMError("Invalid bytecode: Unknown opcode: 0xFF"), "ERR 11"),
        (ValidationError("Unexpected end of bytecode"), "ERR 12"),
        (VMError("Unexpected end of bytecode"), "ERR 12"),
        (ValidationError("Invalid variable index: 8"), "ERR 13"),
        (VMError("Invalid x variable in varpair: 8"), "ERR 13"),
        (ValidationError("Jump from 0 targets invalid address -1"), "ERR 14"),
        (ValidationError("Program can fall past end"), "ERR 14"),
        (ValidationError("Truncated text instruction"), "ERR 15"),
        (VMError("Text contains an unsupported byte"), "ERR 15"),
        (ValidationError("Invalid draw mode: 4"), "ERR 16"),
        (ValidationError("Invalid clear color: 2"), "ERR 16"),
        (ValidationError("Invalid font id: 5"), "ERR 17"),
        (VMError("Invalid font scale: 5"), "ERR 17"),
        (ValidationError("Invalid card sprite id: 129"), "ERR 18"),
        (VMError("Invalid frame 4 for sprite 0"), "ERR 18"),
        (NFCError("Failed reading page 4"), "ERR 19"),
        (OSError("I2C failed"), "ERR 20"),
        (VMError("VM execution failed: index error"), "ERR 21"),
        (AssemblerError("unknown instruction"), "ERR 22"),
        (RuntimeError("Unexpected software failure"), "ERR 99"),
    ],
)
def test_project_errors_map_to_specific_codes(error, code):
    assert classify_error(error) == ERRORS[code]


def test_every_defined_error_has_unique_code_and_title():
    assert len(ERRORS) == 23
    assert len({info.code for info in ERRORS.values()}) == len(ERRORS)
    assert len({info.title for info in ERRORS.values()}) == len(ERRORS)


def test_error_frame_contains_only_stable_user_message():
    first = make_error_frame(RuntimeError("SECRET traceback detail one"))
    second = make_error_frame(RuntimeError("SECRET traceback detail two"))

    assert first.pixels == second.pixels
    assert any(any(row) for row in first.pixels)


class FakeDisplay:
    def __init__(self):
        self.frames = []

    def show(self, framebuffer):
        self.frames.append(framebuffer)


def test_show_error_sends_one_frame_to_display():
    display = FakeDisplay()

    show_error(display, CRCError("private CRC detail"))

    assert len(display.frames) == 1
    assert display.frames[0].pixels == make_error_frame(CRCError("anything")).pixels
