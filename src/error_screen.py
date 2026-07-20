from __future__ import annotations

from dataclasses import dataclass

from src.assembler import AssemblerError
from src.container import CRCError, ContainerError, UnsupportedVersionError
from src.display import DisplayError
from src.framebuffer import FrameBuffer, WIDTH
from src.nfc import NFCError
from src.validator import ValidationError
from src.vm import VMError


@dataclass(frozen=True)
class ErrorInfo:
    code: str
    title: str


ERRORS = {
    "ERR 01": ErrorInfo("ERR 01", "BAD CARD"),
    "ERR 02": ErrorInfo("ERR 02", "BAD CHECKSUM"),
    "ERR 03": ErrorInfo("ERR 03", "BAD VERSION"),
    "ERR 04": ErrorInfo("ERR 04", "BAD PROGRAM"),
    "ERR 05": ErrorInfo("ERR 05", "EXEC LIMIT"),
    "ERR 06": ErrorInfo("ERR 06", "BAD ASSET"),
    "ERR 07": ErrorInfo("ERR 07", "HARDWARE ERROR"),
    "ERR 08": ErrorInfo("ERR 08", "BAD LENGTH"),
    "ERR 09": ErrorInfo("ERR 09", "BAD SPR BANK"),
    "ERR 10": ErrorInfo("ERR 10", "EMPTY PROGRAM"),
    "ERR 11": ErrorInfo("ERR 11", "BAD OPCODE"),
    "ERR 12": ErrorInfo("ERR 12", "TRUNC BYTECODE"),
    "ERR 13": ErrorInfo("ERR 13", "BAD VARIABLE"),
    "ERR 14": ErrorInfo("ERR 14", "BAD JUMP"),
    "ERR 15": ErrorInfo("ERR 15", "BAD TEXT"),
    "ERR 16": ErrorInfo("ERR 16", "BAD DRAW MODE"),
    "ERR 17": ErrorInfo("ERR 17", "BAD FONT"),
    "ERR 18": ErrorInfo("ERR 18", "BAD SPRITE"),
    "ERR 19": ErrorInfo("ERR 19", "NFC ERROR"),
    "ERR 20": ErrorInfo("ERR 20", "DISPLAY ERROR"),
    "ERR 21": ErrorInfo("ERR 21", "VM ERROR"),
    "ERR 22": ErrorInfo("ERR 22", "SOURCE ERROR"),
    "ERR 99": ErrorInfo("ERR 99", "INTERNAL ERROR"),
}


def _container_error(message: str) -> ErrorInfo:
    if "empty code" in message:
        return ERRORS["ERR 10"]

    if any(word in message for word in ("sprite", "encoding", "frame data")):
        return ERRORS["ERR 09"]

    if "extra bytes after" in message:
        return ERRORS["ERR 09"]

    if any(word in message for word in ("length", "truncated", "too large", "too short", "capacity", "exceeds")):
        return ERRORS["ERR 08"]

    return ERRORS["ERR 01"]


def _program_error(message: str) -> ErrorInfo:
    if "execution limit" in message:
        return ERRORS["ERR 05"]

    if "empty program" in message:
        return ERRORS["ERR 10"]

    if "unknown opcode" in message:
        return ERRORS["ERR 11"]

    if "unexpected end" in message or "truncated bytecode" in message:
        return ERRORS["ERR 12"]

    if "variable" in message or "varpair" in message:
        return ERRORS["ERR 13"]

    if "jump" in message or "fall past end" in message or "invalid address" in message:
        return ERRORS["ERR 14"]

    if "text" in message or "unsupported byte" in message:
        return ERRORS["ERR 15"]

    if "draw mode" in message or "clear color" in message:
        return ERRORS["ERR 16"]

    if "font" in message or "scale" in message:
        return ERRORS["ERR 17"]

    if "sprite" in message or "frame" in message:
        return ERRORS["ERR 18"]

    if "asset" in message:
        return ERRORS["ERR 06"]

    if "invalid bytecode data" in message or "vm execution failed" in message:
        return ERRORS["ERR 21"]

    return ERRORS["ERR 04"]


def classify_error(error: Exception) -> ErrorInfo:
    if isinstance(error, CRCError):
        return ERRORS["ERR 02"]

    if isinstance(error, UnsupportedVersionError):
        return ERRORS["ERR 03"]

    if isinstance(error, ContainerError):
        return _container_error(str(error).lower())

    if isinstance(error, AssemblerError):
        return ERRORS["ERR 22"]

    if isinstance(error, ValidationError):
        return _program_error(str(error).lower())

    if isinstance(error, VMError):
        return _program_error(str(error).lower())

    if isinstance(error, NFCError):
        return ERRORS["ERR 19"]

    if error.__class__.__name__ == "HardwareError":
        return ERRORS["ERR 07"]

    if isinstance(error, (DisplayError, OSError)):
        return ERRORS["ERR 20"]

    return ERRORS["ERR 99"]


def _center_x(text: str) -> int:
    width = len(text) * 6 - 1
    return max(0, (WIDTH - width) // 2)


def make_error_frame(error: Exception) -> FrameBuffer:
    info = classify_error(error)
    fb = FrameBuffer()
    fb.clear(0)
    fb.displayText(_center_x(info.title), 12, info.title, 1)
    fb.displayText(_center_x(info.code), 30, info.code, 1)
    return fb


def show_error(display, error: Exception) -> None:
    display.show(make_error_frame(error))
