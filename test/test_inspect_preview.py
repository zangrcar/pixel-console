from types import SimpleNamespace

import pygame
import pytest

from src.container import MAX_NTAG216_BYTES, wrap_program
from src.inspect import inspect_bytes
from src.sprite import Sprite
from src.vm import VMError
from tools.play import collect_frames, should_close
from tools.preview import preview


def test_inspector_reports_v1_crc_size_and_card_sprite(capsys):
    sprite = Sprite(8, 2, 1, [b"\x80\x40"])
    program = wrap_program(bytes([0x00]), [sprite])
    padded = program + bytes(MAX_NTAG216_BYTES - len(program))

    inspect_bytes(padded)
    output = capsys.readouterr().out

    assert f"Total size: {len(program)} bytes" in output
    assert f"Input size: {MAX_NTAG216_BYTES} bytes" in output
    assert "Fits NTAG216: yes" in output
    assert f"Remaining: {MAX_NTAG216_BYTES - len(program)} bytes" in output
    assert "Version: 1" in output
    assert "PXL1 container: yes" in output
    assert "CRC status: ok" in output
    assert "Card sprites: 1" in output
    assert "Sprite 128: 8x2, 1 frame(s)" in output
    assert "Code size: 1 bytes" in output


def test_inspector_ignores_capacity_bytes_after_used_container(capsys):
    program = wrap_program(bytes([0x00]))
    larger_card_read = program + bytes(MAX_NTAG216_BYTES + 100)

    inspect_bytes(larger_card_read)
    output = capsys.readouterr().out

    assert f"Total size: {len(program)} bytes" in output
    assert f"Input size: {len(larger_card_read)} bytes" in output
    assert "Fits NTAG216: yes" in output
    assert "PXL1 container: yes" in output
    assert "CRC status: ok" in output


def test_inspector_reports_bad_crc(capsys):
    program = bytearray(wrap_program(bytes([0x00])))
    program[-1] ^= 0xFF

    inspect_bytes(program)
    output = capsys.readouterr().out

    assert "PXL1 container: no" in output
    assert "CRC status: bad" in output
    assert "Reason: Bad CRC" in output


def write_program(path, source):
    path.write_text(source, encoding="utf-8")
    return str(path)


def test_png_preview_preserves_show_wait_and_frame_ticks(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    source = write_program(
        tmp_path / "timing.pxla",
        "clear 0\nshow\nwait 3\nframe 2\nend\n",
    )

    frames = preview(source)
    output = capsys.readouterr().out

    assert [ticks for _framebuffer, ticks in frames] == [4, 2]
    assert (tmp_path / "output" / "timing.bin").exists()
    assert (tmp_path / "output" / "timing_preview" / "frame_0000.png").exists()
    assert (tmp_path / "output" / "timing_preview" / "frame_0001.png").exists()
    assert "frame_0000.png (4 ticks)" in output
    assert "frame_0001.png (2 ticks)" in output


def test_png_preview_frame_limit_is_configurable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = write_program(
        tmp_path / "loop.pxla",
        "loop:\nframe 1\njmp loop\n",
    )

    frames = preview(source, max_frames=3, max_steps=100)

    assert len(frames) == 3


def test_preview_without_frames_has_clear_message(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    source = write_program(tmp_path / "empty.pxla", "end\n")

    frames = preview(source)

    assert frames == []
    assert "No frames produced" in capsys.readouterr().out


def test_player_collection_preserves_timing(tmp_path):
    source = write_program(
        tmp_path / "timing.pxla",
        "clear 0\nshow\nwait 5\nframe 2\nend\n",
    )

    _input_path, frames = collect_frames(source)

    assert [ticks for _framebuffer, ticks in frames] == [6, 2]


def test_player_collection_stops_infinite_animation_at_max_frames(tmp_path):
    source = write_program(
        tmp_path / "loop.pxla",
        "loop:\nframe 1\njmp loop\n",
    )

    _input_path, frames = collect_frames(source, max_frames=3, max_steps=100)

    assert len(frames) == 3


def test_player_collection_enforces_max_steps_without_frames(tmp_path):
    source = write_program(
        tmp_path / "loop.pxla",
        "loop:\nnop\njmp loop\n",
    )

    with pytest.raises(VMError, match="Execution limit exceeded"):
        collect_frames(source, max_frames=3, max_steps=5)


def test_player_close_events_include_window_close_and_escape():
    assert should_close(SimpleNamespace(type=pygame.QUIT))
    assert should_close(SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert not should_close(SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE))
    assert not should_close(SimpleNamespace(type=pygame.NOEVENT))
