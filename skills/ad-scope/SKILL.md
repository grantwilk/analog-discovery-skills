---
name: ad-scope
description: Capture oscilloscope (Analog In) data from an Analog Discovery in Python with range, offset, sample rate, trigger, and basic statistics. Use for voltage measurements, DC levels, and waveform captures of a few thousand samples.
---

# Oscilloscope capture

Prereq: `ad-connect` template. Inputs are passive, but the user must wire the probes first (`ad-user-handoff`). Longer captures: `ad-scope-record`.

```python
# body: runs inside the ad-connect template
hz, n = 1e6, 4000                                         # sample rate (Hz), samples per channel
dwf.FDwfAnalogInChannelEnableSet(hdwf, -1, 1)             # -1 = all channels
dwf.FDwfAnalogInChannelRangeSet(hdwf, -1, c_double(5))    # full range in volts; nearest supported is used
dwf.FDwfAnalogInChannelOffsetSet(hdwf, -1, c_double(0))
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(hz))
dwf.FDwfAnalogInBufferSizeSet(hdwf, n)
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcDetectorAnalogIn)
dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)
dwf.FDwfAnalogInTriggerChannelSet(hdwf, 0)                # channel 1
dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(0.0))
dwf.FDwfAnalogInTriggerConditionSet(hdwf, DwfTriggerSlopeRise)
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(1))  # capture after 1 s with no trigger; 0 = wait forever
dwf.FDwfAnalogInConfigure(hdwf, 1, 0)                     # apply, do not start
time.sleep(2)                                             # offsets settle after open or range change
dwf.FDwfAnalogInConfigure(hdwf, 0, 1)                     # start
sts = c_byte()
deadline = time.time() + 10
while time.time() < deadline:
    dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
    if sts.value == DwfStateDone.value:
        break
    time.sleep(0.01)
else:
    raise SystemExit("no trigger within 10 s")
ch1 = (c_double * n)()
dwf.FDwfAnalogInStatusData(hdwf, 0, ch1, n)              # channel index 0 = scope 1; 1 = scope 2
v = list(ch1)
print(f"ch1 mean={sum(v)/n:.4f} V  min={min(v):.4f}  max={max(v):.4f}  t_end={n/hz*1e3:.3f} ms")
```

- Time of sample `i` is `i / hz`; with trigger position `0` the trigger sits at the buffer's middle (`FDwfAnalogInTriggerPositionSet`, seconds from the middle).
- Other trigger sources: `trigsrcExternal1/2` (T1/T2 pins), `trigsrcAnalogOut1/2` (see `ad-stimulus-response`), `trigsrcDetectorDigitalIn`, `trigsrcPC`. Conditions: `DwfTriggerSlopeRise|Fall|Either`; types: `trigtypeEdge|Pulse|Transition|Window`.
- Single DC reading: `FDwfAnalogInStatus(hdwf, 1, ...)` then `FDwfAnalogInStatusSample(hdwf, ch, byref(c_double()))`.
- Probe attenuation: `FDwfAnalogInChannelAttenuationSet`. AC coupling on supported devices: `FDwfAnalogInChannelCouplingSet(hdwf, ch, DwfAnalogCouplingAC)`.
- Maximum samples depend on the device configuration: `FDwfAnalogInBufferSizeInfo`, `ad-device-config`.
- Input limits are per model (about ±25 V single-ended on Analog Discovery 2/3). Check the reference manual before connecting anything above 5 V.
- Save or plot the result with `ad-save-and-plot`; frequency content with `ad-spectrum`.

## Docs

- [SDK Reference Manual: Analog In](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [WaveForms SDK guide: scope](https://digilent.com/reference/test-and-measurement/guides/waveforms-sdk-getting-started)
- Samples: `AnalogIn_Acquisition.py`, `AnalogIn_Trigger.py`, `AnalogIn_Triggers.py`, `AnalogIn_Sample.py`, `AnalogIn_Frequency.py`
