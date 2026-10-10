---
name: ad-connect
description: Template for every Python script that controls a Digilent Analog Discovery (or other WaveForms device) through the WaveForms SDK, plus how to list devices, pick one by serial number, and open a demo device with no hardware. Use before writing any other Analog Discovery code.
---

# Connect to a device

Every other `ad-*` skill supplies a `# body` block that goes inside this template. Install first: `ad-install`.

## Template

```python
import glob, math, sys, time
from ctypes import *

# dwfconstants.py: keep it next to the script, or load it from the installed SDK
sys.path += glob.glob(r"C:\Program Files*\Digilent\WaveFormsSDK\samples\py")
sys.path += ["/Applications/WaveForms.app/Contents/Resources/SDK/samples/py",
             "/usr/share/digilent/waveforms/samples/py"]
from dwfconstants import *

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


def last_error():
    msg = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(msg)
    return msg.value.decode()


dwf.FDwfParamSet(DwfParamOnClose, 2)  # on close: 0 keep running, 1 stop instruments, 2 shut down
hdwf = c_int()
dwf.FDwfDeviceOpen(-1, byref(hdwf))   # -1 = first device; use an index to pick another
if hdwf.value == hdwfNone.value:
    raise SystemExit("open failed: " + last_error())
dwf.FDwfDeviceAutoConfigureSet(hdwf, 0)  # settings apply only on FDwf<Instrument>Configure
try:
    pass  # paste a `# body` block here
finally:
    dwf.FDwfDeviceCloseAll()
```

- Every SDK call returns `0` on failure; call `last_error()` to see why.
- Outputs and supplies stay on after the script ends only if `DwfParamOnClose` is `0`. Keep `2` unless the user wants that.
- A device open in the WaveForms app cannot be opened by a script. Close the app first.

## List devices and pick by serial

```python
# body: standalone, run without opening a device
n = c_int()
dwf.FDwfEnum(enumfilterAll, byref(n))
for i in range(n.value):
    name, sn, used = create_string_buffer(64), create_string_buffer(32), c_int()
    dwf.FDwfEnumDeviceName(i, name)
    dwf.FDwfEnumSN(i, sn)
    dwf.FDwfEnumDeviceIsOpened(i, byref(used))
    print(i, name.value.decode(), sn.value.decode(), "in use" if used.value else "free")
```

List before opening: a device your own script has opened is reported as "in use". Open a specific unit by looping `FDwfEnumSN` until it equals `b"SN:XXXXXXXXXXXX"`, then `dwf.FDwfDeviceOpen(i, byref(hdwf))`. Never hard-code the index; indexes change with plug order.

## No hardware: demo devices

The SDK simulates devices. Enumerate with `enumfilterDemo.value | enumfilterType.value` (names end in `DEMO`), then open the index with `FDwfDeviceOpen`. Use this to test code before the user wires anything.

## Docs

- [SDK Reference Manual: Device Enumeration, Device Control](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [Getting Started with the WaveForms SDK](https://digilent.com/reference/test-and-measurement/guides/waveforms-sdk-getting-started)
- Samples: `Device_Enumeration.py`, `Device_Info.py`
