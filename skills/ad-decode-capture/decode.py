"""Decodes UART, SPI, and I2C traffic from Analog Discovery logic analyzer samples."""

from dataclasses import dataclass, field


@dataclass
class UartFrame:
    """One decoded UART character."""

    time_s: float
    value: int
    error: str | None = None


@dataclass
class SpiTransaction:
    """Bytes shifted during one chip-select assertion."""

    time_s: float
    mosi: bytes
    miso: bytes
    leftover_bits: int = 0


@dataclass
class I2cTransaction:
    """One I2C transfer from START to STOP."""

    time_s: float
    address: int
    read: bool
    data: list[int] = field(default_factory=list)
    acks: list[bool] = field(default_factory=list)
    stopped: bool = False


class Decoder:
    """Shared helpers for decoding captured samples."""

    @staticmethod
    def bit(samples: list[int], pin: int) -> list[int]:
        """
        Extracts one DIO pin from the packed samples.

        Args:
            samples (list[int]): Packed samples where bit n is DIO n.
            pin (int): DIO pin number.

        Returns:
            list[int]: The pin level (0 or 1) at each sample.
        """

        return [(s >> pin) & 1 for s in samples]


class UartDecoder(Decoder):
    """Decodes UART characters."""

    @staticmethod
    def decode(
        samples: list[int],
        pin: int,
        sample_rate: float,
        baud: float,
        bits: int = 8,
        parity: str = "none",
        invert: bool = False,
    ) -> list[UartFrame]:
        """
        Decodes UART characters from one pin.

        Args:
            samples (list[int]): Packed samples where bit n is DIO n.
            pin (int): DIO pin carrying the serial line.
            sample_rate (float): Capture sample rate in Hz.
            baud (float): UART bit rate.
            bits (int): Data bits per character.
            parity (str): "none", "even", or "odd".
            invert (bool): True if the line idles low.

        Returns:
            list[UartFrame]: Decoded characters; framing and parity problems set `error`.
        """

        line = [b ^ 1 if invert else b for b in Decoder.bit(samples, pin)]
        per_bit = sample_rate / baud
        frames: list[UartFrame] = []
        i = 1
        while i < len(line):
            if line[i - 1] == 1 and line[i] == 0:
                start = i
                value = 0
                for k in range(bits):
                    idx = int(start + (k + 1.5) * per_bit)
                    if idx >= len(line):
                        return frames
                    value |= line[idx] << k
                pos = bits + 1
                error = None
                if parity != "none":
                    idx = int(start + (pos + 0.5) * per_bit)
                    if idx >= len(line):
                        return frames
                    ones = bin(value).count("1") + line[idx]
                    if (ones % 2 == 1) != (parity == "odd"):
                        error = "parity"
                    pos += 1
                idx = int(start + (pos + 0.5) * per_bit)
                if idx >= len(line):
                    return frames
                if line[idx] != 1 and error is None:
                    error = "framing"
                frames.append(UartFrame(start / sample_rate, value, error))
                i = int(start + (pos + 0.5) * per_bit)
            i += 1
        return frames


class SpiDecoder(Decoder):
    """Decodes SPI transactions."""

    @staticmethod
    def decode(
        samples: list[int],
        cs: int,
        clk: int,
        mosi: int,
        miso: int,
        sample_rate: float,
        mode: int = 0,
        bits: int = 8,
        msb_first: bool = True,
    ) -> list[SpiTransaction]:
        """
        Decodes SPI transactions, with active-low chip select.

        Args:
            samples (list[int]): Packed samples where bit n is DIO n.
            cs (int): DIO pin for chip select.
            clk (int): DIO pin for the clock.
            mosi (int): DIO pin for MOSI.
            miso (int): DIO pin for MISO.
            sample_rate (float): Capture sample rate in Hz.
            mode (int): SPI mode 0 to 3.
            bits (int): Bits per word.
            msb_first (bool): True for MSB-first bit order.

        Returns:
            list[SpiTransaction]: One entry per chip-select assertion.
        """

        cs_line = Decoder.bit(samples, cs)
        clk_line = Decoder.bit(samples, clk)
        mosi_line = Decoder.bit(samples, mosi)
        miso_line = Decoder.bit(samples, miso)
        cpol, cpha = mode >> 1, mode & 1
        sample_on_rising = (cpol == 0) == (cpha == 0)  # modes 0 and 3 sample on the rising edge
        transactions: list[SpiTransaction] = []
        active = False
        start = 0
        words: list[list[int]] = [[], []]
        shift = [0, 0]
        count = 0

        def finish() -> None:
            transactions.append(
                SpiTransaction(
                    start / sample_rate,
                    bytes(words[0]),
                    bytes(words[1]),
                    count,
                )
            )

        for i in range(1, len(samples)):
            if cs_line[i - 1] == 1 and cs_line[i] == 0:
                active, start, count = True, i, 0
                words, shift = [[], []], [0, 0]
            elif cs_line[i - 1] == 0 and cs_line[i] == 1 and active:
                finish()
                active = False
            elif active and clk_line[i] != clk_line[i - 1]:
                rising = clk_line[i] == 1
                if rising == sample_on_rising:
                    for n, line in enumerate((mosi_line, miso_line)):
                        if msb_first:
                            shift[n] = (shift[n] << 1) | line[i]
                        else:
                            shift[n] |= line[i] << count
                    count += 1
                    if count == bits:
                        for n in range(2):
                            words[n].append(shift[n])
                        shift, count = [0, 0], 0
        if active:
            finish()
        return transactions


class I2cDecoder(Decoder):
    """Decodes I2C transactions."""

    @staticmethod
    def decode(
        samples: list[int],
        scl: int,
        sda: int,
        sample_rate: float,
    ) -> list[I2cTransaction]:
        """
        Decodes I2C transactions with 7-bit addressing.

        Args:
            samples (list[int]): Packed samples where bit n is DIO n.
            scl (int): DIO pin for SCL.
            sda (int): DIO pin for SDA.
            sample_rate (float): Capture sample rate in Hz.

        Returns:
            list[I2cTransaction]: One entry per START (or repeated START) to STOP/START.
        """

        scl_line = Decoder.bit(samples, scl)
        sda_line = Decoder.bit(samples, sda)
        transactions: list[I2cTransaction] = []
        current: I2cTransaction | None = None
        bits: list[int] = []
        for i in range(1, len(samples)):
            if scl_line[i] == 1 and scl_line[i - 1] == 1 and sda_line[i] != sda_line[i - 1]:
                if sda_line[i] == 0:  # START or repeated START
                    current = I2cTransaction(i / sample_rate, 0, False)
                    transactions.append(current)
                    bits = []
                elif current is not None:  # STOP
                    current.stopped = True
                    current = None
            elif current is not None and scl_line[i - 1] == 0 and scl_line[i] == 1:
                bits.append(sda_line[i])
                if len(bits) == 9:
                    value = sum(b << (7 - k) for k, b in enumerate(bits[:8]))
                    acked = bits[8] == 0
                    if not current.acks:
                        current.address = value >> 1
                        current.read = bool(value & 1)
                        current.acks.append(acked)
                    else:
                        current.data.append(value)
                        current.acks.append(acked)
                    bits = []
        return transactions
