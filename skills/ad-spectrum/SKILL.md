---
name: ad-spectrum
description: Compute a frequency spectrum (FFT, peak frequency, amplitude) from Analog Discovery scope data in Python. Use for harmonic content, noise, and finding a signal's frequency.
---

# Spectrum analysis

Prereq: `ad-connect` template, `numpy`. Capture with a window of many cycles and a sample rate at least 2.5x the highest frequency of interest.

```python
# body: runs inside the ad-connect template
import numpy as np

hz, n = 1e6, 8192
dwf.FDwfAnalogInChannelEnableSet(hdwf, 0, 1)
dwf.FDwfAnalogInChannelRangeSet(hdwf, 0, c_double(5))
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(hz))
dwf.FDwfAnalogInBufferSizeSet(hdwf, n)
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(1))
dwf.FDwfAnalogInConfigure(hdwf, 1, 0)
time.sleep(2)
dwf.FDwfAnalogInConfigure(hdwf, 0, 1)
sts = c_byte()
while True:
    dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
    if sts.value == DwfStateDone.value:
        break
    time.sleep(0.01)
raw = (c_double * n)()
dwf.FDwfAnalogInStatusData(hdwf, 0, raw, n)

x = np.array(raw) - np.mean(raw)
window = np.hanning(n)
mag = 2 * np.abs(np.fft.rfft(x * window)) / window.sum()      # volts peak per bin
freq = np.fft.rfftfreq(n, 1 / hz)
peak = mag[1:].argmax() + 1
print(f"peak {freq[peak]:.1f} Hz, {mag[peak]:.4f} V peak, {20*np.log10(mag[peak]/1.0):.1f} dBV")
```

- Bin width is `hz / n`. Use `np.fft.rfft` on several captures and average magnitudes to lower the noise floor.
- Leave the DC term out (`mag[1:]`) when looking for peaks.
- The SDK also provides `FDwfSpectrumWindow` and `FDwfSpectrumFFT` if a window or FFT from the SDK is required; sample `AnalogIn_Spectrum.py` shows them.
- Plot with `ad-save-and-plot`.

## Docs

- [SDK Reference Manual: Spectrum functions](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `AnalogIn_FFT.py`, `AnalogIn_Spectrum.py`
