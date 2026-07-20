from pathlib import Path

import pytest

from run import load_program_sprites
from src.assembler import assemble_text
from src.container import MAX_NTAG216_BYTES, unwrap_program, wrap_program
from src.validator import validate_program
from src.vm import PixelVM


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_DIR = ROOT / "prog"
EXAMPLES = sorted(PROGRAM_DIR.glob("*.pxla"))


def build_example(path: Path):
    source = path.read_text(encoding="utf-8")
    code = assemble_text(source, source_name=str(path))
    sprites = load_program_sprites(path)
    container = wrap_program(code, sprites)
    loaded_code, loaded_sprites = unwrap_program(container)
    validate_program(loaded_code, loaded_sprites)
    return code, container, loaded_code, loaded_sprites


def test_utf8_pxla_to_validated_vm_frame_end_to_end():
    path = PROGRAM_DIR / "slovenian_text.pxla"
    code, container, loaded_code, loaded_sprites = build_example(path)
    frames = []

    vm = PixelVM(
        card_sprites=loaded_sprites,
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks)),
    )
    vm.run(loaded_code)

    assert loaded_code == code
    assert len(container) <= MAX_NTAG216_BYTES
    assert bytes([0x80, 0x81, 0x82, 0x20, 0x83, 0x84, 0x85]) in code
    assert len(frames) == 1
    assert any(any(row) for row in frames[0][0].pixels)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda path: path.name)
def test_every_documented_example_builds_fits_ntag216_and_emits_a_frame(path):
    _code, container, loaded_code, loaded_sprites = build_example(path)
    frames = []

    vm = PixelVM(
        card_sprites=loaded_sprites,
        on_frame=lambda framebuffer, ticks: frames.append((framebuffer, ticks)),
    )
    vm.run(loaded_code, max_frames=20, max_steps=10000)

    assert len(container) <= MAX_NTAG216_BYTES
    assert frames
