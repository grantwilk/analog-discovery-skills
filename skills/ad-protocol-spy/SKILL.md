---
name: ad-protocol-spy
description: Passively monitor I2C traffic between two other devices with the Analog Discovery's built-in I2C spy, or record any serial bus (SPI, UART, CAN) with the logic analyzer for later decoding. Use to observe a bus without taking part in it.
---

# Passive bus monitoring

Prereq: `ad-connect` template. Wiring to tell the user (`ad-user-handoff`): connect Analog Discovery DIO pins to the same nets as the bus signals (high-impedance inputs, no effect on the bus) plus `GND` to the bus ground. 3.3 V logic only; use level shifting for 5 V buses.

## I2C (built-in decoder)

```python
# body: runs inside the ad-connect template
dwf.FDwfDigitalI2cReset(hdwf)
dwf.FDwfDigitalI2cRateSet(hdwf, c_double(100e3))     # nominal bus rate
dwf.FDwfDigitalI2cSclSet(hdwf, 0)                    # SCL = DIO0
dwf.FDwfDigitalI2cSdaSet(hdwf, 1)                    # SDA = DIO1
dwf.FDwfDigitalI2cSpyStart(hdwf)
start, stop, nak = c_int(), c_int(), c_int()
data, count = (c_ubyte * 16)(), c_int()
end = time.time() + 10                               # spy for 10 s
while time.time() < end:
    count.value = 16
    if dwf.FDwfDigitalI2cSpyStatus(hdwf, byref(start), byref(stop), byref(data), byref(count), byref(nak)) == 0:
        raise SystemExit(last_error())
    parts = []
    if start.value:
        parts.append("RESTART" if start.value == 2 else "START")
    for i in range(count.value):
        if i == 0 and start.value:
            parts.append(f"addr 0x{data[i] >> 1:02X} {'RD' if data[i] & 1 else 'WR'}")
        else:
            parts.append(f"0x{data[i]:02X}")
    if stop.value:
        parts.append("STOP")
    if nak.value:
        parts.append(f"NAK {nak.value}")
    if parts:
        print(" ".join(parts))
    time.sleep(0.001)
```

## SPI, UART, CAN, and anything else

There is no live spy API for these. Record with the logic analyzer (`ad-logic-analyzer`, record mode for long captures) and decode offline with `ad-decode-capture`. Official SPI spy sample: `DigitalIn_Spi_Spy.py`, `Digital_Spi_Spy.py`.

## Docs

- [SDK Reference Manual: Digital I2C spy, Digital In record](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `Digital_I2c_Spy.py`, `Digital_Spi_Spy.py`, `DigitalIn_Spi_Spy.py`, `DigitalIn_Record.py`
