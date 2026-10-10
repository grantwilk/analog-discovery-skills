---
name: ad-spi
description: Act as an SPI master with an Analog Discovery's DIO pins from Python, writing and reading bytes with configurable mode, bit order, clock, and chip select. Use to talk to SPI sensors, flash, and displays.
---

# SPI master

Prereq: `ad-connect` template. 3.3 V logic only. Wiring to tell the user (`ad-user-handoff`): `DIO0` CS, `DIO1` SCLK, `DIO2` MOSI, `DIO3` MISO, `GND` to target ground, target power from its own supply or `V+` (`ad-supplies`). Passive snooping: `ad-protocol-spy` or `ad-logic-analyzer`.

```python
# body: runs inside the ad-connect template
dwf.FDwfDigitalSpiReset(hdwf)
dwf.FDwfDigitalSpiFrequencySet(hdwf, c_double(1e6))   # SCLK Hz
dwf.FDwfDigitalSpiClockSet(hdwf, 1)                   # SCLK = DIO1
dwf.FDwfDigitalSpiDataSet(hdwf, 0, 2)                 # data line 0 (MOSI) = DIO2
dwf.FDwfDigitalSpiDataSet(hdwf, 1, 3)                 # data line 1 (MISO) = DIO3
dwf.FDwfDigitalSpiModeSet(hdwf, 0)                    # SPI mode 0..3 (CPOL/CPHA)
dwf.FDwfDigitalSpiOrderSet(hdwf, 1)                   # 1 = MSB first, 0 = LSB first
dwf.FDwfDigitalSpiSelectSet(hdwf, 0, 1)               # CS = DIO0, idle high
dwf.FDwfDigitalSpiWriteOne(hdwf, 1, 0, 0)             # take over the pins: drive clock and chip-select idle
time.sleep(0.1)

tx = (c_ubyte * 4)(0x9F, 0, 0, 0)                     # for example a flash JEDEC ID command
rx = (c_ubyte * 4)()
dwf.FDwfDigitalSpiWriteRead(hdwf, 1, 8, tx, len(tx), rx, len(rx))   # 1 = single-wire data, 8 bits per element
print("TX", [hex(b) for b in tx])
print("RX", [hex(b) for b in rx])
```

- `FDwfDigitalSpiWriteRead(hdwf, transferType, bitsPerElement, tx, ntx, rx, nrx)`: `transferType` 1 = standard single-line, 2 = dual, 4 = quad.
- Write-only: `FDwfDigitalSpiWrite(hdwf, 1, 8, tx, len(tx))`. Read-only: `FDwfDigitalSpiRead(hdwf, 1, 8, rx, len(rx))`. Single value of up to 32 bits: `FDwfDigitalSpiWriteOne(hdwf, 1, bits, value)`, `FDwfDigitalSpiReadOne(hdwf, 1, bits, byref(c_uint32()))`.
- `FDwfDigitalSpiSelectSet(hdwf, pin, 0)` makes CS idle low (active-high select). With `FDwfDigitalSpiSelect(hdwf, pin, level)` you control CS manually for transactions that span calls.
- MISO reads all zeros or all ones: wrong mode, wrong wiring, target unpowered, or no common ground. Verify with `ad-logic-analyzer`.
- Stay at or below the target's rated clock; 3.3 V devices only.

## Docs

- [SDK Reference Manual: Digital SPI](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `Digital_Spi.py`, `Digital_Spi_Spy.py`, `Digital_Spi_Dual.py`, `Digital_Spi_Quad.py`
