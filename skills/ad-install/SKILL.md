---
name: ad-install
description: Install the Digilent WaveForms software, runtime, and SDK on Windows, macOS, or Linux so Python can control an Analog Discovery, and verify the install. Use when the dwf library or dwfconstants.py cannot be found, or when setting up a new machine.
---

# Install the toolchain

One download provides everything: drivers, the `dwf` library, the WaveForms app, and the SDK with Python samples. No pip package ships the library.

| OS | Install |
| --- | --- |
| Windows 10+ | Run the `digilent.waveforms_v<ver>_64bit.exe` installer. Keep all components checked. |
| macOS 12+ | Open `digilent.waveforms_v<ver>.dmg` and drag WaveForms to Applications. |
| Linux (deb) | `sudo apt install ./digilent.adept.runtime_*.deb ./digilent.waveforms_*.deb` |
| Linux (rpm) | `sudo yum install ./digilent.adept.runtime_*.rpm ./digilent.waveforms_*.rpm` |

- Download links and the current version: [WaveForms downloads](https://digilent.com/reference/software/waveforms/waveforms-3/previous-versions). Digilent may ask for an email; ask the user to download, or check whether the installer is already on the machine.
- Linux needs the Adept Runtime installed separately. Reinstall it after an OS update if the device stops being detected (udev rules can be deleted).
- Match architecture to the machine (x64, ARM64, Raspberry Pi builds are listed on the download page).
- Full OS-specific walkthrough: [WaveForms Getting Started Guide](https://digilent.com/reference/software/waveforms/waveforms-3/getting-started-guide).

## Where things land

| | `dwf` library | `dwfconstants.py` and samples |
| --- | --- | --- |
| Windows | `dwf.dll` in `System32` | `C:\Program Files\Digilent\WaveFormsSDK\samples\py` (older installers: `Program Files (x86)`) |
| macOS | `/Library/Frameworks/dwf.framework/dwf` | `/Applications/WaveForms.app/Contents/Resources/SDK/samples/py` |
| Linux | `libdwf.so` | `/usr/share/digilent/waveforms/samples/py` |

The SDK reference manual PDF is in the SDK folder next to `samples`.

## Verify

```python
import glob, sys
from ctypes import *

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(32)
dwf.FDwfGetVersion(version)
print("DWF version:", version.value.decode())
print("constants:", glob.glob(r"C:\Program Files*\Digilent\WaveFormsSDK\samples\py\dwfconstants.py")
      + glob.glob("/usr/share/digilent/waveforms/samples/py/dwfconstants.py")
      + glob.glob("/Applications/WaveForms.app/Contents/Resources/SDK/samples/py/dwfconstants.py"))
```

If it prints a version and a path, continue with `ad-connect`. Otherwise see `ad-troubleshoot`.

## Optional Python packages

`pip install numpy matplotlib` is enough for analysis and plots. Do not use the `WF_SDK` package from Digilent's `WaveForms-SDK-Getting-Started-PY` repository: it has not been updated since 2022 and breaks on current constants. Third-party wrappers exist (for example [dwfpy](https://pypi.org/project/dwfpy/)) but these skills use the official `ctypes` interface so they work with any SDK version.
