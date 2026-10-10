---
name: ad-wavegen-custom
description: Output an arbitrary custom waveform (from a list of samples, a formula, or a file) on an Analog Discovery's W1 or W2 from Python. Use when standard waveforms are not enough.
---

# Custom waveform

Prereq: `ad-connect` template. **Outputs drive the user's circuit**; confirm wiring first (`ad-user-handoff`).

```python
# body: runs inside the ad-connect template
ch = 0                                                    # 0 = W1, 1 = W2
low, high = c_int(), c_int()
dwf.FDwfAnalogOutNodeDataInfo(hdwf, ch, AnalogOutNodeCarrier, byref(low), byref(high))
n = min(high.value, 4096)                                 # samples in one period of the pattern
samples = (c_double * n)()
for i in range(n):
    samples[i] = math.sin(2 * math.pi * i / n) * 0.5 + 0.5 * math.sin(6 * math.pi * i / n)  # any formula, -1 to +1
dwf.FDwfAnalogOutNodeEnableSet(hdwf, ch, AnalogOutNodeCarrier, 1)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, ch, AnalogOutNodeCarrier, funcCustom)
dwf.FDwfAnalogOutNodeDataSet(hdwf, ch, AnalogOutNodeCarrier, samples, n)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, ch, AnalogOutNodeCarrier, c_double(1e3))  # repetitions of the whole buffer per second
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, ch, AnalogOutNodeCarrier, c_double(1.0))  # data of +1 outputs this many volts
dwf.FDwfAnalogOutNodeOffsetSet(hdwf, ch, AnalogOutNodeCarrier, c_double(0.0))
dwf.FDwfAnalogOutConfigure(hdwf, ch, 1)
time.sleep(5)
dwf.FDwfAnalogOutConfigure(hdwf, ch, 0)
```

- Sample values are normalized to **-1 to +1**; `Amplitude` scales them to volts. Do not put volts in the array.
- The buffer size limit depends on the device configuration (`FDwfAnalogOutNodeDataInfo`, `ad-device-config`).
- Load samples from a file with `numpy.loadtxt`, scale to ±1 by dividing by the peak, then copy into the `c_double` array.
- Streaming or long non-repeating waveforms ("play" mode): `FDwfAnalogOutNodeFunctionSet(..., funcPlay)` and `FDwfAnalogOutNodePlayData`; follow samples `AnalogOut_Play.py`, `AnalogOutIn_PlayRecord.py`.
- Play the signal while recording another: `AnalogOutIn_PlayRecord.py`, `AnalogOutIn_RecordPlay.py`.

## Docs

- [SDK Reference Manual: Analog Out, custom and play data](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `AnalogOut_Custom.py`, `AnalogOut_Play.py`, `AnalogOut_DualBuffer.py`
