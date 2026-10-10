"""Tests for the offline protocol decoders bundled with the ad-decode-capture skill."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "ad-decode-capture"))

from decode import I2cDecoder, SpiDecoder, UartDecoder  # noqa: E402


class WaveformBuilder:
    """Builds packed logic samples with named pins for decoder tests."""

    def __init__(self, idle: dict[int, int]) -> None:
        """
        Initializes the builder.

        Args:
            idle (dict[int, int]): Idle level of each used pin, keyed by DIO number.
        """

        self.levels = dict(idle)
        self.samples: list[int] = []

    def hold(self, count: int, **changes: int) -> None:
        """
        Holds the current levels for some samples after applying changes.

        Args:
            count (int): Number of samples to emit.
            **changes (int): New pin levels, such as `p0=1`.
        """

        for name, level in changes.items():
            self.levels[int(name[1:])] = level
        value = sum(level << pin for pin, level in self.levels.items())
        self.samples.extend([value] * count)


class TestUartDecoder:
    """Tests for UartDecoder."""

    PER_BIT = 10

    def _frame(self, builder: WaveformBuilder, value: int, bits: int, parity: str | None,
               stop_level: int = 1) -> None:
        builder.hold(self.PER_BIT, p0=0)
        for k in range(bits):
            builder.hold(self.PER_BIT, p0=(value >> k) & 1)
        if parity:
            ones = bin(value).count("1")
            builder.hold(self.PER_BIT, p0=(ones % 2) ^ (1 if parity == "odd" else 0))
        builder.hold(self.PER_BIT, p0=stop_level)
        builder.hold(self.PER_BIT, p0=1)

    @pytest.mark.parametrize(
        ("bits", "parity", "payload"),
        [(8, None, b"Hi!"), (7, "even", b"AZ"), (8, "odd", b"\x00\xff")],
    )
    def test_decodes_characters(self, bits: int, parity: str | None, payload: bytes) -> None:
        """Valid frames decode to the transmitted values without errors."""

        builder = WaveformBuilder({0: 1})
        builder.hold(30, p0=1)
        for byte in payload:
            self._frame(builder, byte & ((1 << bits) - 1), bits, parity)
        frames = UartDecoder.decode(
            builder.samples, 0, 1000.0, 100.0, bits=bits, parity=parity or "none"
        )
        assert [f.value for f in frames] == [b & ((1 << bits) - 1) for b in payload]
        assert all(f.error is None for f in frames)

    def test_flags_framing_and_parity_errors(self) -> None:
        """A low stop bit is a framing error; wrong parity is a parity error."""

        builder = WaveformBuilder({0: 1})
        builder.hold(30, p0=1)
        self._frame(builder, 0x55, 8, None, stop_level=0)
        builder.hold(40, p0=1)
        framed = UartDecoder.decode(builder.samples, 0, 1000.0, 100.0)
        assert framed[0].error == "framing"

        builder = WaveformBuilder({0: 1})
        builder.hold(30, p0=1)
        self._frame(builder, 0x01, 8, "odd")
        wrong = UartDecoder.decode(builder.samples, 0, 1000.0, 100.0, parity="even")
        assert wrong[0].error == "parity"


class TestSpiDecoder:
    """Tests for SpiDecoder."""

    @staticmethod
    def _transfer(mode: int, mosi: bytes, miso: bytes, msb_first: bool) -> list[int]:
        """Builds a CS=p0, CLK=p1, MOSI=p2, MISO=p3 transfer in the given mode."""

        cpol, cpha = mode >> 1, mode & 1
        builder = WaveformBuilder({0: 1, 1: cpol, 2: 0, 3: 0})
        builder.hold(5)
        builder.hold(5, p0=0)
        for out, back in zip(mosi, miso, strict=True):
            order = range(7, -1, -1) if msb_first else range(8)
            for k in order:
                a, b = (out >> k) & 1, (back >> k) & 1
                if cpha == 0:
                    builder.hold(4, p2=a, p3=b)
                    builder.hold(4, p1=cpol ^ 1)
                    builder.hold(4, p1=cpol)
                else:
                    builder.hold(4, p1=cpol ^ 1)
                    builder.hold(4, p2=a, p3=b)
                    builder.hold(4, p1=cpol)
        builder.hold(5)
        builder.hold(5, p0=1)
        return builder.samples

    @pytest.mark.parametrize("mode", [0, 1, 2, 3])
    @pytest.mark.parametrize("msb_first", [True, False])
    def test_decodes_modes_and_bit_order(self, mode: int, msb_first: bool) -> None:
        """Every SPI mode and bit order recovers both data lines."""

        mosi, miso = b"\x9f\x00\xa5", b"\x00\xc2\x3c"
        samples = self._transfer(mode, mosi, miso, msb_first)
        result = SpiDecoder.decode(
            samples, 0, 1, 2, 3, 1e6, mode=mode, msb_first=msb_first
        )
        assert len(result) == 1
        assert result[0].mosi == mosi
        assert result[0].miso == miso
        assert result[0].leftover_bits == 0


class TestI2cDecoder:
    """Tests for I2cDecoder."""

    @staticmethod
    def _byte(builder: WaveformBuilder, value: int, ack: bool) -> None:
        """Emits one byte plus ACK/NAK bit on SCL=p0, SDA=p1."""

        bits = [(value >> k) & 1 for k in range(7, -1, -1)] + [0 if ack else 1]
        for bit in bits:
            builder.hold(4, p0=0, p1=bit)
            builder.hold(4, p0=1)

    def _transaction(self, builder: WaveformBuilder, address: int, read: bool,
                     data: list[int], acks: list[bool]) -> None:
        builder.hold(8, p0=1, p1=1)
        builder.hold(4, p1=0)
        self._byte(builder, (address << 1) | read, acks[0])
        for value, ack in zip(data, acks[1:], strict=True):
            self._byte(builder, value, ack)
        builder.hold(4, p0=0, p1=0)
        builder.hold(4, p0=1)
        builder.hold(4, p1=1)

    def test_decodes_write_then_read(self) -> None:
        """Address, direction, data, ACKs, and STOP are recovered per transaction."""

        builder = WaveformBuilder({0: 1, 1: 1})
        self._transaction(builder, 0x1D, False, [0x0D, 0x7F], [True, True, True])
        self._transaction(builder, 0x50, True, [0xAA], [True, False])
        result = I2cDecoder.decode(builder.samples, 0, 1, 1e6)
        assert [(t.address, t.read, t.data, t.acks, t.stopped) for t in result] == [
            (0x1D, False, [0x0D, 0x7F], [True, True, True], True),
            (0x50, True, [0xAA], [True, False], True),
        ]

    def test_address_nak(self) -> None:
        """A NAK on the address byte is reported as a False first ACK."""

        builder = WaveformBuilder({0: 1, 1: 1})
        self._transaction(builder, 0x20, False, [], [False])
        result = I2cDecoder.decode(builder.samples, 0, 1, 1e6)
        assert result[0].address == 0x20
        assert result[0].acks == [False]
