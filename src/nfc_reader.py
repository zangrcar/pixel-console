from __future__ import annotations

MAX_NTAG216_BYTES = 888


class NFCError(Exception):
    pass


class NFCReader:
    def __init__(self):
        import board
        import busio
        from adafruit_pn532.i2c import PN532_I2C

        i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(i2c, debug=False)

        ic, ver, rev, support = self.pn532.firmware_version
        self.pn532.SAM_configuration()

    def wait_for_card(self):
        while True:
            uid = self.pn532.read_passive_target(timeout=0.5)
            if uid is not None:
                return uid

    def read_ntag216_user_memory(self) -> bytes:
        data = bytearray()

        # NTAG216 user memory starts at page 4.
        # 222 user pages * 4 bytes = 888 bytes.
        for page in range(4, 4 + 222):
            block = self.pn532.ntag2xx_read_block(page)

            if block is None:
                raise NFCError(f"Failed reading page {page}")

            data.extend(block[:4])

        return bytes(data[:MAX_NTAG216_BYTES])