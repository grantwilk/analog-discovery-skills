---
name: ad-pattern-generator
description: Generate digital patterns on an Analog Discovery's DIO pins from Python, including clocks, pulses, PWM, counters, random data, and custom bit sequences. Use for timed digital stimulus.
---

# Pattern generator

Prereq: `ad-connect` template. **Enabled DIO pins drive the user's circuit at 3.3 V.** Tell the user which pins and `GND` to connect (`ad-user-handoff`).

## Clock / PWM

```python
# body: runs inside the ad-connect template
pin = 0
base = c_double()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(base))
dwf.FDwfDigitalOutEnableSet(hdwf, pin, 1)
dwf.FDwfDigitalOutTypeSet(hdwf, pin, DwfDigitalOutTypePulse)
dwf.FDwfDigitalOutDividerSet(hdwf, pin, int(base.value / 1e3))   # counter ticks at 1 kHz; one period = low + high ticks
dwf.FDwfDigitalOutCounterSet(hdwf, pin, 3, 1)                    # 3 ticks low, 1 tick high = 250 Hz at 25 % duty
dwf.FDwfDigitalOutConfigure(hdwf, 1)
time.sleep(5)
dwf.FDwfDigitalOutConfigure(hdwf, 0)
```

- Output frequency = `base / divider / (low + high)`. Pick a large `low + high` for fine duty-cycle resolution and a smaller divider.
- Initial state, start delay, and polarity: `FDwfDigitalOutCounterInitSet(hdwf, pin, start_high, start_counter)`, `FDwfDigitalOutIdleSet(hdwf, pin, DwfDigitalOutIdleLow)`.

## Custom bit sequence (data pattern)

```python
# body: runs inside the ad-connect template
pin, bits = 1, "1100101000"                                      # sent LSB-first per byte below
base = c_double()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(base))
n = len(bits)
data = (c_ubyte * ((n + 7) // 8))()
for i, b in enumerate(bits):
    if b == "1":
        data[i // 8] |= 1 << (i % 8)
dwf.FDwfDigitalOutEnableSet(hdwf, pin, 1)
dwf.FDwfDigitalOutTypeSet(hdwf, pin, DwfDigitalOutTypeCustom)
dwf.FDwfDigitalOutDividerSet(hdwf, pin, int(base.value / 1e4))   # 10 kbit/s
dwf.FDwfDigitalOutDataSet(hdwf, pin, byref(data), n)             # bit count
dwf.FDwfDigitalOutRepeatSet(hdwf, 1)                             # 0 = forever
dwf.FDwfDigitalOutRunSet(hdwf, c_double(n / 1e4))
dwf.FDwfDigitalOutConfigure(hdwf, 1)
time.sleep(n / 1e4 + 0.1)
```

- Other pin types: `DwfDigitalOutTypeRandom`, `DwfDigitalOutTypeState`, `DwfDigitalOutTypePlay` (streamed).
- Multi-pin buses, counters, and 'play' mode: see samples `DigitalOut_BinrayCounter.py`, `DigitalOut_CustomBus.py`, `DigitalOut_Play.py`.
- Start from a trigger or in sync with other instruments: `FDwfDigitalOutTriggerSourceSet(hdwf, trigsrcExternal1)`.
- Static levels: `ad-static-io`. Protocol traffic (UART, SPI, I2C, CAN): their own skills.

## Docs

- [SDK Reference Manual: Digital Out](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `DigitalOut_Clock.py`, `DigitalOut_Pulse.py`, `DigitalOut_Custom.py`, `DigitalOut_Duty.py`, `DigitalOut_Pins.py`
