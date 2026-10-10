---
name: ad-stimulus-response
description: Drive a circuit with the wavegen and capture the response with the scope, hardware-synchronized so the capture starts exactly when the output starts. Use for step and pulse response, filter testing, and any stimulus-then-measure test.
---

# Stimulus and response

Prereq: `ad-connect` template. Wiring (confirm with the user, `ad-user-handoff`): `W1` to the circuit input and scope `1+`; circuit output to scope `2+`; scope `1-`, `2-` and circuit ground to `GND`.

```python
# body: runs inside the ad-connect template
hz, n = 1e6, 8192
# stimulus: one 1 kHz sine burst on W1, started later by software
dwf.FDwfAnalogOutNodeEnableSet(hdwf, 0, AnalogOutNodeCarrier, 1)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, 0, AnalogOutNodeCarrier, funcSine)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, 0, AnalogOutNodeCarrier, c_double(1e3))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, 0, AnalogOutNodeCarrier, c_double(1.0))
dwf.FDwfAnalogOutRunSet(hdwf, 0, c_double(2e-3))          # 2 cycles
dwf.FDwfAnalogOutRepeatSet(hdwf, 0, 1)
# scope: armed on W1 start, with 30 % of the buffer before it
dwf.FDwfAnalogInChannelEnableSet(hdwf, -1, 1)
dwf.FDwfAnalogInChannelRangeSet(hdwf, -1, c_double(5))
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(hz))
dwf.FDwfAnalogInBufferSizeSet(hdwf, n)
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcAnalogOut1)
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(0.3 * n / hz))
dwf.FDwfAnalogInConfigure(hdwf, 1, 1)                     # apply and arm
sts = c_byte()
while True:
    dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
    if sts.value == DwfStateArmed.value:
        break
    time.sleep(0.01)
time.sleep(2)                                             # offsets settle
dwf.FDwfAnalogOutConfigure(hdwf, 0, 1)                    # start W1: the scope triggers with it
while True:
    dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
    if sts.value == DwfStateDone.value:
        break
    time.sleep(0.01)
stimulus, response = (c_double * n)(), (c_double * n)()
dwf.FDwfAnalogInStatusData(hdwf, 0, stimulus, n)
dwf.FDwfAnalogInStatusData(hdwf, 1, response, n)
print(f"stimulus peak {max(stimulus):.3f} V, response peak {max(response):.3f} V")
```

- Trigger other instruments from a pin: `FDwfDeviceTriggerSet(hdwf, 0, trigsrcAnalogOut1)` drives `T1`; the scope or logic analyzer then uses `trigsrcExternal1` (also for two devices, sample `AnalogOutIn_Synchronization.py`).
- Other trigger sources: `trigsrcDigitalOut`, `trigsrcDetectorDigitalIn`, `trigsrcPC`.
- Sweep response: `ad-network-analyzer`. Plot with `ad-save-and-plot`.

## Docs

- [SDK Reference Manual: Analog In trigger sources, Analog Out](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `AnalogOutIn_Synchronization.py`, `AnalogOut_Sweep.py`, `AnalogInOut_Trigger.py`, `AnalogOutIn_Transfer.py`
