---
name: ad-network-analyzer
description: Measure frequency response (Bode gain and phase) of a circuit with an Analog Discovery's network analyzer, swept in Python. Use for filters, amplifiers, and transfer functions.
---

# Network analyzer (Bode)

Prereq: `ad-connect` template, `numpy`. Wiring (confirm with the user, `ad-user-handoff`): `W1` to the circuit input and scope `1+`; circuit output to scope `2+`; scope `1-`, `2-` and circuit ground to `GND`. A reference resistor in series is needed only for impedance modes (`ad-impedance`).

```python
# body: runs inside the ad-connect template
import numpy as np

start, stop, steps, amplitude = 1e2, 1e6, 41, 1.0            # Hz, Hz, points, volts peak
dwf.FDwfDeviceAutoConfigureSet(hdwf, 3)                      # allow settings to change while running
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, 0)                      # network-analyzer wiring
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(1e4))     # ohms, unused for a pure gain measurement
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(start))
dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(amplitude))
dwf.FDwfAnalogImpedanceConfigure(hdwf, 1)
time.sleep(2)

freqs = np.logspace(np.log10(start), np.log10(stop), steps)
gain_db, phase_deg = [], []
status = c_byte()
for hz in freqs:
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz))
    time.sleep(0.01)
    dwf.FDwfAnalogImpedanceStatus(hdwf, None)                # discard the capture from the old frequency
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(status)) == 0:
            raise SystemExit(last_error())
        if status.value == 2:
            break
    g1, g2, ph2 = c_double(), c_double(), c_double()
    dwf.FDwfAnalogImpedanceStatusInput(hdwf, 0, byref(g1), None)   # channel 1 relative to the generated signal
    dwf.FDwfAnalogImpedanceStatusInput(hdwf, 1, byref(g2), byref(ph2))  # channel 2 relative to channel 1
    gain_db.append(-20 * np.log10(g2.value))                 # output / input
    phase_deg.append(-ph2.value * 180 / np.pi)
dwf.FDwfAnalogImpedanceConfigure(hdwf, 0)
for hz, g, p in zip(freqs, gain_db, phase_deg):
    print(f"{hz:12.1f} Hz  {g:8.2f} dB  {p:8.2f} deg")
```

- The gain math follows the official sample (`1/gain`); verify on a known circuit (for example a resistor divider reads its ratio) before trusting numbers.
- Alternative without the impedance API: step `W1` frequency with `ad-wavegen`, capture both channels with `ad-scope`, and compute gain and phase from an FFT (`ad-spectrum`).
- Plot with `ad-save-and-plot` using a log frequency axis.

## Docs

- [SDK Reference Manual: Analog Impedance](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [WaveForms Network Analyzer instrument](https://files.digilent.com/manuals/WaveForms/3.25.1/main.html) (application manual; pick the matching version)
- Samples: `AnalogNetwork_Analyzer.py`, `AnalogImpedance_Analyzer.py`
