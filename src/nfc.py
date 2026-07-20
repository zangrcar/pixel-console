from __future__ import annotations

from src.container import MAX_NTAG216_BYTES, unwrap_program

NTAG216_FIRST_USER_PAGE = 4
NTAG216_USER_PAGE_COUNT = 222
NTAG216_PAGE_SIZE = 4
PN532_UART_BAUDRATE = 115200
PN532_UART_TIMEOUT = 0.1


class NFCError(Exception):
    pass


class NFCReader:
    def __init__(self, pn532=None):
        try:
            if pn532 is None:
                import board
                import busio
                from adafruit_pn532.uart import PN532_UART

                uart = busio.UART(
                    board.TX,
                    board.RX,
                    baudrate=PN532_UART_BAUDRATE,
                    timeout=PN532_UART_TIMEOUT,
                )
                pn532 = PN532_UART(uart, debug=False)

            self.pn532 = pn532
            self.firmware_version = tuple(self.pn532.firmware_version)
            self.pn532.SAM_configuration()
        except Exception as error:
            raise NFCError("Failed to initialize PN532 UART") from error

    def wait_for_card(self, timeout=0.5):
        while True:
            try:
                uid = self.pn532.read_passive_target(timeout=timeout)

                if uid is not None:
                    return bytes(uid)
            except Exception as error:
                raise NFCError("Failed detecting NFC card") from error

    def wait_for_removal(self, timeout=0.2, missed_reads=2) -> None:
        if missed_reads < 1:
            raise ValueError("missed_reads must be at least 1")

        misses = 0

        while misses < missed_reads:
            try:
                uid = self.pn532.read_passive_target(timeout=timeout)
            except Exception as error:
                raise NFCError("Failed checking NFC card removal") from error

            if uid is None:
                misses += 1
            else:
                misses = 0

    def read_ntag216_user_memory(self) -> bytes:
        data = bytearray()

        for page in range(
            NTAG216_FIRST_USER_PAGE,
            NTAG216_FIRST_USER_PAGE + NTAG216_USER_PAGE_COUNT,
        ):
            try:
                block = self.pn532.ntag2xx_read_block(page)

                if block is None or len(block) < NTAG216_PAGE_SIZE:
                    raise NFCError(f"Failed reading page {page}")

                data.extend(block[:NTAG216_PAGE_SIZE])
            except NFCError:
                raise
            except Exception as error:
                raise NFCError(f"Failed reading page {page}") from error

        return bytes(data[:MAX_NTAG216_BYTES])

    def write_ntag216_user_memory(self, data: bytes) -> None:
        try:
            data = bytes(data)
        except (TypeError, ValueError) as error:
            raise NFCError(f"Invalid NFC data: {error}") from error

        if len(data) > MAX_NTAG216_BYTES:
            raise NFCError("Data too large for NTAG216")

        padded = data + bytes(MAX_NTAG216_BYTES - len(data))

        for index in range(NTAG216_USER_PAGE_COUNT):
            page = NTAG216_FIRST_USER_PAGE + index
            start = index * NTAG216_PAGE_SIZE
            chunk = padded[start:start + NTAG216_PAGE_SIZE]

            try:
                ok = self.pn532.ntag2xx_write_block(page, chunk)
            except Exception as error:
                raise NFCError(f"Failed writing page {page}") from error

            if not ok:
                raise NFCError(f"Failed writing page {page}")

    def verify_ntag216_user_memory(self, expected: bytes) -> bytes:
        try:
            expected = bytes(expected)
        except (TypeError, ValueError) as error:
            raise NFCError(f"Invalid NFC data: {error}") from error

        if len(expected) > MAX_NTAG216_BYTES:
            raise NFCError("Data too large for NTAG216")

        actual = self.read_ntag216_user_memory()

        if actual[:len(expected)] != expected:
            mismatch = next(
                index
                for index, (written, read) in enumerate(zip(expected, actual))
                if written != read
            )
            raise NFCError(f"NFC verify mismatch at byte {mismatch}")

        unwrap_program(actual)

        return actual[:len(expected)]

    def write_and_verify(self, data: bytes) -> bytes:
        try:
            data = bytes(data)
        except (TypeError, ValueError) as error:
            raise NFCError(f"Invalid NFC data: {error}") from error

        # Reject a damaged container before touching the card.
        unwrap_program(data)
        self.write_ntag216_user_memory(data)
        return self.verify_ntag216_user_memory(data)
