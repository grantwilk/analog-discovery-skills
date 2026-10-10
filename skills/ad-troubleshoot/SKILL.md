---
name: ad-troubleshoot
description: Diagnose why an Analog Discovery script fails: device not found, cannot open, library or constants missing, no data, timeouts, or outdated sample code. Use whenever an ad-* script errors or returns nothing.
---

# Troubleshooting

First step for every failure: print the SDK's own message.

```python
msg = create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(msg)
print(msg.value.decode())
```

| Symptom | Fix |
| --- | --- |
| `OSError`/cannot load `dwf` | WaveForms not installed or wrong architecture: `ad-install` |
| `FDwfEnum` returns zero devices | Cable or hub; another app has it open (close WaveForms); Linux: Adept Runtime missing or udev rules removed by an OS update, reinstall it; `ad-connect` lists devices |
| Open fails: "device is in use" | Close the WaveForms app and any other Python process (`FDwfDeviceCloseAll()` at the end of every script) |
| Open fails with a configuration error | Unplug and replug; use `FDwfEnumDeviceIsOpened` to see ownership |
| Scope reads an offset or noisy first capture | Wait 2 s after `Configure` before starting (offset settles) |
| Scope never triggers | Use `FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(1))`, or check trigger channel, level, and condition |
| Settings have no effect | Missed `Configure` (`FDwfDeviceAutoConfigureSet(hdwf, 0)` means settings apply only on Configure) |
| Outputs stop after the script ends | Expected; see `DwfParamOnClose` in `ad-connect` |
| Digital pins read all `0` or `1` | No ground, no pull-up, wrong pin number, or 5 V level where 3.3 V is allowed |
| Protocol read returns garbage or NAK | Wrong rate, mode, polarity, address (I2C address is passed shifted left one bit), or missing pull-ups; capture with `ad-logic-analyzer` and decode with `ad-decode-capture` |
| `numpy.float` / `AttributeError: time.clock` in Digilent samples | Samples are stale: use `float` / `time.time()` or `time.perf_counter()` |
| Sample rate or buffer smaller than requested | The SDK clamps to device limits: read back with `FDwfAnalogInFrequencyGet`, `FDwfAnalogInBufferSizeGet`; change configuration with `ad-device-config` |
| Need to test without hardware | Open a demo device (`ad-connect`) |

If the problem persists, look up the exact function in the [SDK Reference Manual](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual) and compare with the sample of the same name in the SDK `samples/py` folder; the [Digilent forum](https://forum.digilent.com/) has an active WaveForms section.
