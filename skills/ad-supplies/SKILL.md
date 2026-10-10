---
name: ad-supplies
description: Control the programmable power supplies (V+ and V-) and read system monitors (USB and AUX voltage, current, temperature) on an Analog Discovery from Python. Use to power a circuit under test or to check the device's own power state.
---

# Power supplies and monitors

Prereq: `ad-connect` template. **Enabling a supply powers the user's circuit.** Confirm what is connected to `V+`/`V-`, the voltage, and the current budget first (`ad-user-handoff`). Never short `V+`/`V-` to anything or to each other.

## List channels and nodes (names differ per model)

```python
# body: runs inside the ad-connect template
channels = c_int()
dwf.FDwfAnalogIOChannelCount(hdwf, byref(channels))
for ch in range(channels.value):
    name, label, nodes = create_string_buffer(32), create_string_buffer(16), c_int()
    dwf.FDwfAnalogIOChannelName(hdwf, ch, name, label)
    dwf.FDwfAnalogIOChannelInfo(hdwf, ch, byref(nodes))
    for node in range(nodes.value):
        node_name, units = create_string_buffer(32), create_string_buffer(16)
        dwf.FDwfAnalogIOChannelNodeName(hdwf, ch, node, node_name, units)
        print(ch, name.value.decode(), "node", node, node_name.value.decode(), units.value.decode())
```

## Enable ±5 V and read back

On Analog Discovery 2 and 3: channel 0 is `V+`, channel 1 is `V-`; node 0 is enable, node 1 is voltage, node 2 is the measured current.

```python
# body: runs inside the ad-connect template
dwf.FDwfAnalogIOChannelNodeSet(hdwf, 0, 0, c_double(1))      # V+ enable
dwf.FDwfAnalogIOChannelNodeSet(hdwf, 0, 1, c_double(5.0))    # V+ volts
dwf.FDwfAnalogIOChannelNodeSet(hdwf, 1, 0, c_double(1))      # V- enable
dwf.FDwfAnalogIOChannelNodeSet(hdwf, 1, 1, c_double(-5.0))   # V- volts
dwf.FDwfAnalogIOEnableSet(hdwf, 1)                           # master enable
time.sleep(1)
dwf.FDwfAnalogIOStatus(hdwf)                                 # refresh readings
vplus, vminus, master = c_double(), c_double(), c_int()
dwf.FDwfAnalogIOChannelNodeStatus(hdwf, 0, 1, byref(vplus))
dwf.FDwfAnalogIOChannelNodeStatus(hdwf, 1, 1, byref(vminus))
dwf.FDwfAnalogIOEnableStatus(hdwf, byref(master))            # 0 = a supply tripped (overcurrent)
print(f"V+={vplus.value:.3f} V  V-={vminus.value:.3f} V  enabled={master.value}")
dwf.FDwfAnalogIOEnableSet(hdwf, 0)                           # supplies off
```

## Device monitors

Monitor channels have "Monitor" in their name (USB voltage, current, temperature; AUX voltage, current). Node names and indexes differ per model, so read by name:

```python
# body: runs inside the ad-connect template
dwf.FDwfAnalogIOStatus(hdwf)
channels = c_int()
dwf.FDwfAnalogIOChannelCount(hdwf, byref(channels))
for ch in range(channels.value):
    name, label, nodes = create_string_buffer(32), create_string_buffer(16), c_int()
    dwf.FDwfAnalogIOChannelName(hdwf, ch, name, label)
    if b"Monitor" not in name.value:
        continue
    dwf.FDwfAnalogIOChannelInfo(hdwf, ch, byref(nodes))
    for node in range(nodes.value):
        node_name, units, value = create_string_buffer(32), create_string_buffer(16), c_double()
        dwf.FDwfAnalogIOChannelNodeName(hdwf, ch, node, node_name, units)
        dwf.FDwfAnalogIOChannelNodeStatus(hdwf, ch, node, byref(value))
        print(f"{name.value.decode()} {node_name.value.decode()}: {value.value:.3f} {units.value.decode()}")
```

- Read the supply current with node 2 (`FDwfAnalogIOChannelNodeStatus(hdwf, 0, 2, ...)`).
- Supplies stop on overcurrent; re-arm with `FDwfAnalogIOEnableSet(hdwf, 0)` then `1`.
- USB power alone limits the available current; an external AUX supply raises it. Limits per model are in the reference manuals.
- Supplies turn off when the script closes unless `DwfParamOnClose` is `0`.

## Docs

- [SDK Reference Manual: Analog IO](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [Analog Discovery 2 reference manual](https://digilent.com/reference/test-and-measurement/analog-discovery-2/reference-manual), [Analog Discovery 3 reference manual](https://digilent.com/reference/test-and-measurement/analog-discovery-3/reference-manual)
- Samples: `AnalogIO_AnalogDiscovery2_Power.py`, `AnalogIO_AnalogDiscovery3_Power.py`, `AnalogIO_AnalogDiscovery2_SystemMonitor.py` (other models have their own `AnalogIO_*` samples)
