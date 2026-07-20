import pytest

from src.assembler import AssemblerError, assemble_file, assemble_text


@pytest.mark.parametrize(
    "source, line_number, message",
    [
        ("clear 0\nexplode 1", 2, "unknown instruction: explode"),
        ("rect 1 2", 1, "rect expects 4 args, got 2"),
        ("jmp missing", 1, "unknown label: missing"),
        ("loop:\nnop\nloop:\nend", 3, "duplicate label: loop"),
        (":\nend", 1, "empty label"),
        ("spr 0 0 MISSING 0", 1, "unknown sprite name: MISSING"),
        ("setv 8 1", 1, "variable must be 0..7"),
        ("clear 256", 1, "u8 out of range: 256"),
        ("move -129 0", 1, "i8 out of range: -129"),
        ("font 5 1", 1, "font id must be 0..4"),
        ("font 0 5", 1, "font scale must be 1..4"),
        (f'text 0 0 "{"A" * 65}"', 1, "text too long, max 64 bytes"),
        ('text 0 0 "Cena 10 €"', 1, "Unsupported character '€'"),
    ],
)
def test_assembler_errors_include_source_line(source, line_number, message):
    problem_line = source.splitlines()[line_number - 1]

    with pytest.raises(AssemblerError) as error_info:
        assemble_text(source, source_name="gift.pxla")

    error = error_info.value

    assert error.source_name == "gift.pxla"
    assert error.line_number == line_number
    assert error.source_line == problem_line
    assert message in str(error)
    assert f"gift.pxla: Line {line_number}" in str(error)
    assert f"    {problem_line}" in str(error)


def test_rel16_out_of_range_has_jump_line_context():
    source = "jmp far\n" + "nop\n" * 32768 + "far:\nend\n"

    with pytest.raises(AssemblerError) as error_info:
        assemble_text(source, source_name="large.pxla")

    assert "large.pxla: Line 1" in str(error_info.value)
    assert "rel16 out of range: 32768" in str(error_info.value)
    assert "    jmp far" in str(error_info.value)


def test_comment_markers_inside_quoted_text_are_preserved():
    code = assemble_text(
        'text 0 0 "TI SI #1; // OK" ; this is a real comment\nend'
    )
    stored_text = b"TI SI #1; // OK"

    assert code[:4] == bytes([0x15, 0, 0, len(stored_text)])
    assert code[4:4 + len(stored_text)] == stored_text
    assert code[-1] == 0x00


@pytest.mark.parametrize("marker", ["#", ";", "//"])
def test_each_comment_marker_still_works_outside_string(marker):
    assert assemble_text(f"clear 0 {marker} comment\nend") == bytes([0x02, 0, 0])


def test_assemble_file_uses_input_filename_in_error(tmp_path):
    source = tmp_path / "broken.pxla"
    output = tmp_path / "broken.bin"
    source.write_text("clear 999\n", encoding="utf-8")

    with pytest.raises(AssemblerError) as error_info:
        assemble_file(source, output)

    assert str(source) in str(error_info.value)
    assert "Line 1" in str(error_info.value)
    assert "clear 999" in str(error_info.value)
    assert not output.exists()
