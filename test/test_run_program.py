import subprocess
import sys
from pathlib import Path


def test_run_program_cli(tmp_path):
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "demo.pxla"
    source.write_text("end\n", encoding="utf-8")
    output = tmp_path / "demo.bin"

    result = subprocess.run(
        [sys.executable, str(root / "run.py"), str(source), "--output", str(output)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output.exists()


def test_run_program_with_bare_name(tmp_path):
    root = Path(__file__).resolve().parents[1]
    prog_dir = tmp_path / "prog"
    output_dir = tmp_path / "output"
    prog_dir.mkdir()
    output_dir.mkdir()
    (prog_dir / "demo.pxla").write_text("end\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(root / "run.py"), "demo"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "demo.bin").exists()


def test_build_only_writes_bin_without_executing_program(tmp_path):
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "build_only.pxla"
    source.write_text("pset 1 1\nshow\nend\n", encoding="utf-8")
    output = tmp_path / "build_only.bin"

    result = subprocess.run(
        [
            sys.executable,
            str(root / "run.py"),
            str(source),
            "--output",
            str(output),
            "--build-only",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output.exists()
    assert not (tmp_path / "output" / "frame_0000.png").exists()
