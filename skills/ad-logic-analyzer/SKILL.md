---
name: ad-logic-analyzer
description: Capture digital signals on an Analog Discovery's DIO pins from Python with sample rate, trigger, and analysis of edges, frequency, and duty cycle. Use for timing, bus bring-up, and checking whether a signal toggles.
---

# Logic analyzer

Prereq: `ad-connect` template. DIO is 3.3 V logic; tell the user which DIO pins to connect plus `GND` (`ad-user-handoff`). Protocol decoding: `ad-decode-capture`.

```python
# body: runs inside the ad-connect template
n = 8192
base = c_double()
dwf.FDwfDigitalInInternalClockInfo(hdwf, byref(base))        # internal clock, e.g. 100e6 or 800e6
want_hz = 1e6
dwf.FDwfDigitalInDividerSet(hdwf, int(round(base.value / want_hz)))   # sample rate = clock / divider
dwf.FDwfDigitalInSampleFormatSet(hdwf, 16)                   # bits per sample: 8, 16 or 32 (16 = DIO0..15)
dwf.FDwfDigitalInBufferSizeSet(hdwf, n)
dwf.FDwfDigitalInTriggerSourceSet(hdwf, trigsrcDetectorDigitalIn)
dwf.FDwfDigitalInTriggerPositionSet(hdwf, n // 2)            # samples kept after the trigger
dwf.FDwfDigitalInTriggerSet(hdwf, 0, 0, 1 << 0, 0)           # level low, level high, rise, fall: here rising edge on DIO0
dwf.FDwfDigitalInTriggerAutoTimeoutSet(hdwf, c_double(1))    # capture anyway after 1 s without a trigger; 0 = wait forever
dwf.FDwfDigitalInConfigure(hdwf, 0, 1)
sts = c_byte()
deadline = time.time() + 5
while time.time() < deadline:
    dwf.FDwfDigitalInStatus(hdwf, 1, byref(sts))
    if sts.value == DwfStateDone.value:
        break
    time.sleep(0.01)
else:
    raise SystemExit("capture did not finish within 5 s")
raw = (c_uint16 * n)()
dwf.FDwfDigitalInStatusData(hdwf, raw, 2 * n)                # buffer size in bytes
samples = list(raw)                                          # bit k of each sample is DIO k
dio0 = [(s >> 0) & 1 for s in samples]
edges = sum(1 for a, b in zip(dio0, dio0[1:]) if a != b)
rate = base.value / round(base.value / want_hz)
print(f"{n} samples at {rate:.0f} Hz, DIO0 edges: {edges}, high {sum(dio0)/n:.1%}")
```

- Trigger on an input condition: `FDwfDigitalInTriggerSet(hdwf, level_low_mask, level_high_mask, edge_rise_mask, edge_fall_mask)`. With a timeout of `0` the capture waits forever for the trigger.
- Trigger source `trigsrcNone` + `FDwfDigitalInConfigure(hdwf, 0, 1)` captures immediately; `trigsrcExternal1` uses the T1 pin; `trigsrcAnalogIn` follows the scope trigger.
- Long captures or streaming: set `FDwfDigitalInAcquisitionModeSet(hdwf, acqmodeRecord)` and read with `FDwfDigitalInStatusRecord`; follow sample `DigitalIn_Record.py`.
- Max buffer and sample rates depend on the device configuration: `ad-device-config`.
- Save or plot with `ad-save-and-plot`.

## Docs

- [SDK Reference Manual: Digital In](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `DigitalIn_Acquisition.py`, `DigitalIn_Trigger.py`, `DigitalIn_Record.py`
