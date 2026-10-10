---
name: ad-device-config
description: List and select an Analog Discovery device configuration, which trades buffer sizes between the scope, wavegen, logic analyzer, and pattern generator. Use when a capture or waveform needs more samples than the default buffer allows.
---

# Device configurations

Some devices expose several configurations that reallocate memory between instruments. Configuration `0` is the default that `FDwfDeviceOpen` uses. Pick another only when a buffer is too small.

```python
# body: standalone, run without opening a device
n = c_int()
dwf.FDwfEnum(enumfilterAll, byref(n))
for dev in range(n.value):
    cfgs = c_int()
    dwf.FDwfEnumConfig(dev, byref(cfgs))
    for cfg in range(cfgs.value):
        row = []
        for label, info in [("AnalogIn", DECIAnalogInBufferSize), ("AnalogOut", DECIAnalogOutBufferSize),
                            ("DigitalIn", DECIDigitalInBufferSize), ("DigitalOut", DECIDigitalOutBufferSize)]:
            size = c_int()
            dwf.FDwfEnumConfigInfo(cfg, info, byref(size))
            row.append(f"{label} {size.value}")
        print(f"device {dev} config {cfg}: " + ", ".join(row))
```

Open with a chosen configuration instead of `FDwfDeviceOpen` in the `ad-connect` template:

```python
dwf.FDwfDeviceConfigOpen(-1, 1, byref(hdwf))   # device index, configuration index
```

Check the actual limits after opening with `FDwfAnalogInBufferSizeInfo`, `FDwfAnalogOutNodeDataInfo`, `FDwfDigitalInBufferSizeInfo`, and `FDwfDigitalOutDataInfo`.

## Docs

- [SDK Reference Manual: Device Control and the per-device chapters](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [Analog Discovery 2 reference manual: device configurations](https://digilent.com/reference/test-and-measurement/analog-discovery-2/reference-manual)
- [Analog Discovery 3 reference manual: device configuration](https://digilent.com/reference/test-and-measurement/analog-discovery-3/reference-manual)
- Samples: `Device_Enumeration.py`, `AnalogIn_Buffers.py`
