---
name: ad-wavegen
description: Generate standard analog waveforms (sine, square, triangle, DC, noise, ramps, pulse) and sweeps on an Analog Discovery's W1 and W2 outputs from Python. Use to drive a circuit with a stimulus signal.
---

# Waveform generator

Prereq: `ad-connect` template. **Outputs drive the user's circuit.** Confirm wiring and amplitude with the user first (`ad-user-handoff`). Arbitrary shapes: `ad-wavegen-custom`.

```python
# body: runs inside the ad-connect template
ch = 0                                                       # 0 = W1, 1 = W2, -1 = both
dwf.FDwfAnalogOutNodeEnableSet(hdwf, ch, AnalogOutNodeCarrier, 1)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, ch, AnalogOutNodeCarrier, funcSine)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, ch, AnalogOutNodeCarrier, c_double(1e3))   # Hz
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, ch, AnalogOutNodeCarrier, c_double(1.0))   # volts peak: 1 V = 2 Vpp
dwf.FDwfAnalogOutNodeOffsetSet(hdwf, ch, AnalogOutNodeCarrier, c_double(0.0))      # volts
dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, ch, AnalogOutNodeCarrier, c_double(50))     # percent
dwf.FDwfAnalogOutNodePhaseSet(hdwf, ch, AnalogOutNodeCarrier, c_double(0))         # degrees
dwf.FDwfAnalogOutConfigure(hdwf, ch, 1)                      # 1 = start, 0 = stop
time.sleep(5)                                                # output runs while the script is open
dwf.FDwfAnalogOutConfigure(hdwf, ch, 0)
```

- Functions: `funcDC` (set `Offset`), `funcSine`, `funcSquare`, `funcTriangle`, `funcRampUp`, `funcRampDown`, `funcNoise`, `funcPulse`, `funcTrapezium`.
- Run a limited burst: `FDwfAnalogOutRunSet(hdwf, ch, seconds)`, `FDwfAnalogOutWaitSet(hdwf, ch, seconds)` before the run, `FDwfAnalogOutRepeatSet(hdwf, ch, count)` (0 = forever).
- Output idle level between bursts: `FDwfAnalogOutIdleSet(hdwf, ch, DwfAnalogOutIdleOffset)`.
- To keep the output running after the script exits set `DwfParamOnClose` to `0` in the template (and tell the user).
- Peak amplitude is limited to about 5 V; check the model's limits in its reference manual.
- Start W1 and W2 together or trigger them from other instruments: `FDwfAnalogOutTriggerSourceSet`, `ad-stimulus-response`.

## Sweep (frequency modulation)

```python
# body: 1 kHz to 20 kHz sine sweep over 5 ms on W1, frequency-modulated by a ramp
lo, hi, sweep_s = 1e3, 20e3, 5e-3
mid = (lo + hi) / 2
ch = 0
dwf.FDwfAnalogOutNodeEnableSet(hdwf, ch, AnalogOutNodeCarrier, 1)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, ch, AnalogOutNodeCarrier, funcSine)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, ch, AnalogOutNodeCarrier, c_double(mid))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, ch, AnalogOutNodeCarrier, c_double(1.0))
dwf.FDwfAnalogOutNodeEnableSet(hdwf, ch, AnalogOutNodeFM, 1)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, ch, AnalogOutNodeFM, funcRampUp)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, ch, AnalogOutNodeFM, c_double(1 / sweep_s))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, ch, AnalogOutNodeFM, c_double(100 * (hi - mid) / mid))  # percent
dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, ch, AnalogOutNodeFM, c_double(100))
dwf.FDwfAnalogOutRunSet(hdwf, ch, c_double(sweep_s))
dwf.FDwfAnalogOutRepeatSet(hdwf, ch, 1)
dwf.FDwfAnalogOutConfigure(hdwf, ch, 1)
time.sleep(sweep_s + 0.1)
```

Amplitude modulation uses `AnalogOutNodeAM` the same way. Measuring a sweep response: `ad-stimulus-response`, `ad-network-analyzer`.

## Docs

- [SDK Reference Manual: Analog Out](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `AnalogOut_Sine.py`, `AnalogOut_Sweep.py`, `AnalogOut_Pulse.py`, `AnalogOut_Phase.py`, `AnalogOut_Delay.py`, `AnalogOut_Sync.py`
