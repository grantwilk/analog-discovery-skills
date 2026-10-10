---
name: ad-impedance
description: Measure impedance, resistance, capacitance, and inductance of a component with an Analog Discovery's impedance analyzer from Python. Use for component characterization with the Impedance Analyzer adapter or a reference resistor.
---

# Impedance analyzer

Prereq: `ad-connect` template. Needs either the Digilent Impedance Analyzer adapter (mode `8`) or a known reference resistor wired as in the manual (modes `0` or `1`). Describe the exact wiring to the user (`ad-user-handoff`) before measuring.

```python
# body: runs inside the ad-connect template
hz, reference = 1e3, 1e3                                  # test frequency (Hz), reference resistor (ohms)
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, 8)                   # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = adapter
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference))
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz))
dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1))    # volts peak
dwf.FDwfAnalogImpedanceConfigure(hdwf, 1)
time.sleep(1)
dwf.FDwfAnalogImpedanceStatus(hdwf, None)                 # discard the stale capture
status = c_byte()
while True:
    if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(status)) == 0:
        raise SystemExit(last_error())
    if status.value == 2:
        break
for label, measure in [("|Z| ohm", DwfAnalogImpedanceImpedance), ("phase rad", DwfAnalogImpedanceImpedancePhase),
                       ("R ohm", DwfAnalogImpedanceResistance), ("X ohm", DwfAnalogImpedanceReactance),
                       ("Cs F", DwfAnalogImpedanceSeriesCapacitance), ("Ls H", DwfAnalogImpedanceSeriesInductance)]:
    value = c_double()
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, measure, byref(value))
    print(f"{label:>10}: {value.value:.6g}")
dwf.FDwfAnalogImpedanceConfigure(hdwf, 0)
```

- Other measures: `DwfAnalogImpedanceParallelCapacitance`, `ParallelInductance`, `Dissipation`, `Quality`, `Admittance`, `Conductance`, `Susceptance`, `Vrms`, `Irms`.
- Pick a reference resistor near the expected `|Z|`, and a test frequency where the part behaves as intended.
- Frequency sweeps and compensation: samples `AnalogImpedance_Analyzer.py`, `AnalogImpedance_Compensation.py`.

## Docs

- [SDK Reference Manual: Analog Impedance](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [WaveForms Impedance Analyzer instrument](https://files.digilent.com/manuals/WaveForms/3.25.1/main.html) (application manual; pick the matching version)
- Samples: `AnalogImpedance_Measure.py`, `AnalogImpedance_Meter.py`, `AnalogImpedance_Average.py`
