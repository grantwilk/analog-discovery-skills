---
name: ad-decode-capture
description: Decode UART, SPI, and I2C traffic from Analog Discovery logic analyzer samples in Python using the bundled decode.py. Use to see what bytes were on a bus, verify a protocol, or debug a link that fails.
---

# Decode a capture

Prereq: a logic capture from `ad-logic-analyzer` (`samples` = list of packed 16-bit ints, bit n = DIO n; `rate` = actual sample rate in Hz). Capture at **at least 8 samples per bit** (UART), or **8 samples per clock period** (SPI, I2C). `decode.py` sits next to this `SKILL.md`; add its folder to `sys.path` or copy it beside the script.

```python
# body: standalone, after a capture
from decode import I2cDecoder, SpiDecoder, UartDecoder

for f in UartDecoder.decode(samples, pin=1, sample_rate=rate, baud=115200):
    print(f"{f.time_s*1e3:9.3f} ms  0x{f.value:02X}  {chr(f.value) if 32 <= f.value < 127 else '.'}  {f.error or ''}")

for t in SpiDecoder.decode(samples, cs=0, clk=1, mosi=2, miso=3, sample_rate=rate, mode=0):
    print(f"{t.time_s*1e3:9.3f} ms  MOSI {t.mosi.hex(' ')}  MISO {t.miso.hex(' ')}")

for t in I2cDecoder.decode(samples, scl=0, sda=1, sample_rate=rate):
    print(f"{t.time_s*1e3:9.3f} ms  addr 0x{t.address:02X} {'R' if t.read else 'W'}  "
          f"data {[hex(b) for b in t.data]}  acks {t.acks}  {'STOP' if t.stopped else ''}")
```

- UART parameters: `bits`, `parity` (`"none"`, `"even"`, `"odd"`), `invert`. Errors appear as `"framing"` or `"parity"`.
- SPI: active-low CS; `mode` 0 to 3; `bits`; `msb_first`. Any `leftover_bits` indicates a frame length not divisible by `bits`.
- I2C: 7-bit address. `acks[0]` is the address ACK; the rest correspond to `data`. `False` means NAK.
- Empty results usually mean the sample rate is too low, the pins are wrong, or the signal did not toggle; check with `ad-save-and-plot`.
- Live protocol traffic (not captured): `ad-uart`, `ad-spi`, `ad-i2c`, `ad-can`, `ad-protocol-spy`. CAN decoding is not provided offline.

## Docs

- [WaveForms Logic Analyzer protocol decoders (GUI reference)](https://digilent.com/reference/software/waveforms/waveforms-3/reference-manual)
