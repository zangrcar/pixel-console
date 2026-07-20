import sys
from types import ModuleType

import pytest

from src.container import CRCError, MAX_NTAG216_BYTES, unwrap_program, wrap_program
from src.nfc import (
    NFCError,
    NFCReader,
    NTAG216_FIRST_USER_PAGE,
    NTAG216_PAGE_SIZE,
    NTAG216_USER_PAGE_COUNT,
    PN532_UART_BAUDRATE,
    PN532_UART_TIMEOUT,
)
from tools.write_card import load_program


class FakePN532:
    def __init__(self, memory=None, targets=None):
        self.firmware_version = (0x32, 1, 6, 7)
        self.memory = bytearray(memory or bytes(MAX_NTAG216_BYTES))
        self.targets = list(targets or [])
        self.sam_calls = 0
        self.target_calls = []
        self.read_pages = []
        self.write_pages = []
        self.fail_sam = False
        self.fail_read_page = None
        self.short_read_page = None
        self.raise_read_page = None
        self.fail_write_page = None
        self.raise_write_page = None

    def SAM_configuration(self):
        if self.fail_sam:
            raise OSError("SAM failed")
        self.sam_calls += 1

    def read_passive_target(self, timeout=0.5):
        self.target_calls.append(timeout)

        if not self.targets:
            return None

        result = self.targets.pop(0)

        if isinstance(result, Exception):
            raise result

        return result

    def ntag2xx_read_block(self, page):
        self.read_pages.append(page)

        if page == self.raise_read_page:
            raise OSError("read failed")

        if page == self.fail_read_page:
            return None

        if page == self.short_read_page:
            return b"\x00\x01\x02"

        start = (page - NTAG216_FIRST_USER_PAGE) * NTAG216_PAGE_SIZE
        return bytes(self.memory[start:start + NTAG216_PAGE_SIZE])

    def ntag2xx_write_block(self, page, data):
        self.write_pages.append((page, bytes(data)))

        if page == self.raise_write_page:
            raise OSError("write failed")

        if page == self.fail_write_page:
            return False

        start = (page - NTAG216_FIRST_USER_PAGE) * NTAG216_PAGE_SIZE
        self.memory[start:start + NTAG216_PAGE_SIZE] = data
        return True


def make_reader(fake=None):
    fake = fake or FakePN532()
    return NFCReader(pn532=fake), fake


def test_default_transport_uses_pn532_uart_on_raspberry_pi_pins(monkeypatch):
    fake = FakePN532()
    tx_pin = object()
    rx_pin = object()
    uart_calls = []
    pn532_calls = []
    uart_object = object()

    board_module = ModuleType("board")
    board_module.TX = tx_pin
    board_module.RX = rx_pin

    busio_module = ModuleType("busio")

    def make_uart(tx, rx, **kwargs):
        uart_calls.append((tx, rx, kwargs))
        return uart_object

    busio_module.UART = make_uart

    pn532_package = ModuleType("adafruit_pn532")
    pn532_uart_module = ModuleType("adafruit_pn532.uart")

    def make_pn532(uart, debug=False):
        pn532_calls.append((uart, debug))
        return fake

    pn532_uart_module.PN532_UART = make_pn532

    monkeypatch.setitem(sys.modules, "board", board_module)
    monkeypatch.setitem(sys.modules, "busio", busio_module)
    monkeypatch.setitem(sys.modules, "adafruit_pn532", pn532_package)
    monkeypatch.setitem(sys.modules, "adafruit_pn532.uart", pn532_uart_module)

    reader = NFCReader()

    assert reader.pn532 is fake
    assert uart_calls == [
        (
            tx_pin,
            rx_pin,
            {"baudrate": PN532_UART_BAUDRATE, "timeout": PN532_UART_TIMEOUT},
        )
    ]
    assert pn532_calls == [(uart_object, False)]


def test_fake_pn532_is_configured_and_firmware_is_recorded():
    reader, fake = make_reader()

    assert reader.firmware_version == fake.firmware_version
    assert fake.sam_calls == 1


def test_initialization_failure_becomes_nfc_error():
    fake = FakePN532()
    fake.fail_sam = True

    with pytest.raises(NFCError, match="initialize PN532 UART"):
        NFCReader(pn532=fake)


def test_wait_for_card_ignores_misses_and_returns_uid():
    reader, fake = make_reader(FakePN532(targets=[None, None, b"\x01\x02\x03\x04"]))

    assert reader.wait_for_card(timeout=0.01) == b"\x01\x02\x03\x04"
    assert fake.target_calls == [0.01, 0.01, 0.01]


def test_wait_for_card_driver_failure_becomes_nfc_error():
    reader, _fake = make_reader(FakePN532(targets=[OSError("PN532 timeout")]))

    with pytest.raises(NFCError, match="detecting NFC card"):
        reader.wait_for_card()


def test_wait_for_removal_requires_consecutive_misses():
    uid = b"\x01\x02\x03\x04"
    reader, fake = make_reader(FakePN532(targets=[uid, None, uid, None, None]))

    reader.wait_for_removal(timeout=0.01, missed_reads=2)

    assert fake.target_calls == [0.01] * 5


def test_wait_for_removal_rejects_invalid_debounce_count():
    reader, _fake = make_reader()

    with pytest.raises(ValueError, match="at least 1"):
        reader.wait_for_removal(missed_reads=0)


def test_read_returns_all_888_ntag216_user_bytes():
    memory = bytes(index % 256 for index in range(MAX_NTAG216_BYTES))
    reader, fake = make_reader(FakePN532(memory=memory))

    assert reader.read_ntag216_user_memory() == memory
    assert fake.read_pages == list(range(4, 226))


@pytest.mark.parametrize("failure", ["fail_read_page", "short_read_page", "raise_read_page"])
def test_page_read_failures_become_nfc_error(failure):
    reader, fake = make_reader()
    setattr(fake, failure, 37)

    with pytest.raises(NFCError, match="reading page 37"):
        reader.read_ntag216_user_memory()


def test_write_fills_all_user_pages_and_clears_unused_capacity():
    reader, fake = make_reader()
    data = b"PXL1 test"

    reader.write_ntag216_user_memory(data)

    assert len(fake.write_pages) == NTAG216_USER_PAGE_COUNT
    assert fake.write_pages[0][0] == 4
    assert fake.write_pages[-1][0] == 225
    assert bytes(fake.memory[:len(data)]) == data
    assert not any(fake.memory[len(data):])


@pytest.mark.parametrize("failure", ["fail_write_page", "raise_write_page"])
def test_page_write_failures_become_nfc_error(failure):
    reader, fake = make_reader()
    setattr(fake, failure, 91)

    with pytest.raises(NFCError, match="writing page 91"):
        reader.write_ntag216_user_memory(b"test")


def test_oversized_write_is_rejected_before_accessing_card():
    reader, fake = make_reader()

    with pytest.raises(NFCError, match="too large for NTAG216"):
        reader.write_ntag216_user_memory(bytes(MAX_NTAG216_BYTES + 1))

    assert fake.write_pages == []


def test_write_read_compare_and_crc_verification_round_trip():
    program = wrap_program(b"\x00")
    reader, fake = make_reader()

    verified = reader.write_and_verify(program)
    code, sprites = unwrap_program(bytes(fake.memory))

    assert verified == program
    assert code == b"\x00"
    assert sprites == []
    assert len(fake.write_pages) == 222
    assert len(fake.read_pages) == 222


def test_verify_reports_first_different_byte():
    program = wrap_program(b"\x00")
    reader, fake = make_reader()
    reader.write_ntag216_user_memory(program)
    fake.memory[7] ^= 0x01

    with pytest.raises(NFCError, match="mismatch at byte 7"):
        reader.verify_ntag216_user_memory(program)


def test_verify_checks_container_crc_after_byte_comparison():
    program = bytearray(wrap_program(b"\x00"))
    program[-1] ^= 0xFF
    reader, fake = make_reader()
    fake.memory[:len(program)] = program

    with pytest.raises(CRCError, match="Bad CRC"):
        reader.verify_ntag216_user_memory(bytes(program))


def test_bin_loader_ignores_zero_capacity_after_used_container(tmp_path):
    program = wrap_program(b"\x00")
    path = tmp_path / "card.bin"
    path.write_bytes(program + bytes(MAX_NTAG216_BYTES - len(program)))

    assert load_program(str(path)) == program
