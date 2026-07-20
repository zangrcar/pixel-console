import signal
from pathlib import Path

import pytest

from src import device


ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = ROOT / "systemd" / "pixel-console.service.template"
INSTRUCTIONS_PATH = ROOT / "systemd" / "README.md"


def test_service_uses_absolute_venv_paths_and_required_restart_settings():
    service = SERVICE_PATH.read_text(encoding="utf-8")

    assert "User=<USERNAME>" in service
    assert "WorkingDirectory=/home/<USERNAME>/pixel_console" in service
    assert (
        "ExecStart=/home/<USERNAME>/pixel_console/.venv/bin/python -m src.device"
        in service
    )
    assert "Restart=on-failure" in service
    assert "RestartSec=2" in service
    assert "StandardOutput=journal" in service
    assert "StandardError=journal" in service
    assert "WantedBy=multi-user.target" in service
    assert "~" not in service
    assert "source " not in service


def test_installation_instructions_require_checks_and_manual_execstart():
    instructions = INSTRUCTIONS_PATH.read_text(encoding="utf-8")

    assert "whoami" in instructions
    assert "pwd" in instructions
    assert ".venv/bin/python --version" in instructions
    assert (
        "/home/<USERNAME>/pixel_console/.venv/bin/python -m src.device"
        in instructions
    )
    assert "systemctl daemon-reload" in instructions
    assert "systemctl enable" in instructions
    assert "systemctl status" in instructions
    assert "journalctl -u pixel-console.service" in instructions


def test_main_registers_sigterm_and_exits_cleanly_on_shutdown(monkeypatch):
    handlers = {}

    def register_handler(signum, handler):
        handlers[signum] = handler

    def interrupted_console():
        raise KeyboardInterrupt

    monkeypatch.setattr(device.signal, "signal", register_handler)
    monkeypatch.setattr(device, "run_console", interrupted_console)

    device.main()

    assert handlers[signal.SIGTERM] is device._handle_shutdown

    with pytest.raises(KeyboardInterrupt):
        handlers[signal.SIGTERM](signal.SIGTERM, None)
