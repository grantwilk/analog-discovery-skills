---
name: ad-static-io
description: Read and write the Analog Discovery's digital I/O pins (DIO 0-15) as static levels from Python, like the WaveForms Static I/O instrument. Use for GPIO, LEDs, switches, reset lines, and simple on/off control.
---

# Static digital I/O

Prereq: `ad-connect` template. DIO is **3.3 V logic** on Analog Discovery 2/3; do not connect 5 V signals. Common ground is required: tell the user to connect `GND` (`ad-user-handoff`).

```python
# body: runs inside the ad-connect template
dwf.FDwfDigitalIOReset(hdwf)
pins = [0, 1, 2, 3]                                   # DIO pins to drive
out_mask = sum(1 << p for p in pins)
dwf.FDwfDigitalIOOutputEnableSet(hdwf, out_mask)      # bit set = output, clear = input (high impedance)
dwf.FDwfDigitalIOOutputSet(hdwf, 0b0101)              # drive DIO0 high, DIO1 low, DIO2 high, DIO3 low
dwf.FDwfDigitalIOConfigure(hdwf)
time.sleep(0.1)
dwf.FDwfDigitalIOStatus(hdwf)                         # refresh the input snapshot
levels = c_uint32()
dwf.FDwfDigitalIOInputStatus(hdwf, byref(levels))
print(f"DIO15..0 = {levels.value:016b}")              # bit n = DIO n; outputs read back what the pin sees
```

- Read one pin: `(levels.value >> n) & 1`. Read-only pins: leave them out of the output mask.
- Pull resistors on supported models: `FDwfDigitalIOPullSet(hdwf, pull_up_mask, pull_down_mask)`.
- Drive strength and slew on supported models: `FDwfDigitalIODriveInfo`, `FDwfDigitalIODriveSet`.
- Pins hold their level until the script ends; with `DwfParamOnClose` = `2` (template default) all pins return to high impedance on exit.
- Fast or timed signals: `ad-pattern-generator`. Capturing a signal over time: `ad-logic-analyzer`.

## Docs

- [SDK Reference Manual: Digital IO](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `DigitalIO.py`
