import subprocess
import sys
from pathlib import Path


def test_run_program_cli(tmp_path):
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "demo.pxla"
    source.write_text("end\n", encoding="utf-8")
    output = tmp_path / "demo.bin"

    result = subprocess.run(
        [sys.executable, str(root / "run_program.py"), str(source), "--output", str(output)],
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
        [sys.executable, str(root / "run_program.py"), "demo"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "demo.bin").exists()
