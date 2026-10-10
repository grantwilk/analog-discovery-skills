---
name: ad-overview
description: Entry point and index of skills for controlling a Digilent Analog Discovery (or other WaveForms device) from Python with the WaveForms SDK. Use at the start of any task involving an Analog Discovery, scope, wavegen, logic analyzer, supplies, or bus protocols.
---

# Analog Discovery skills

These skills let an agent do from Python what a human does in the WaveForms GUI. They wrap the official WaveForms SDK (`dwf` via `ctypes`); they do not teach electronics or Digilent hardware.

## Workflow

1. Install once: `ad-install`.
2. Every script starts from the `ad-connect` template.
3. Anything with wiring: send the user the `ad-user-handoff` message and wait.
4. Run the script, read the numbers, plot if useful (`ad-save-and-plot`).
5. Errors: `ad-troubleshoot`.

## Skill index

| Goal | Skill |
| --- | --- |
| Install the software and SDK | `ad-install` |
| Detect devices, open one, demo devices | `ad-connect` |
| Buffer configurations | `ad-device-config` |
| Ask the user to wire something | `ad-user-handoff` |
| Voltage capture, triggers | `ad-scope` |
| Long recordings | `ad-scope-record` |
| Sine, square, triangle, DC, sweeps | `ad-wavegen` |
| Arbitrary waveform | `ad-wavegen-custom` |
| Power supplies and device monitors | `ad-supplies` |
| FFT and spectrum | `ad-spectrum` |
| Bode plot | `ad-network-analyzer` |
| R, L, C, impedance | `ad-impedance` |
| Output then measure, synchronized | `ad-stimulus-response` |
| Digital pin read and write | `ad-static-io` |
| Logic analyzer capture | `ad-logic-analyzer` |
| Digital patterns, clock, PWM | `ad-pattern-generator` |
| UART | `ad-uart` |
| SPI master | `ad-spi` |
| I2C master and scan | `ad-i2c` |
| CAN | `ad-can` |
| Passive I2C spy | `ad-protocol-spy` |
| Decode UART, SPI, I2C from a capture | `ad-decode-capture` |
| CSV and PNG output | `ad-save-and-plot` |

## Rules for agents

- Do not guess SDK names. Every function and constant used in these skills exists in the installed SDK headers (`dwf.h`, `dwfconstants.py`); anything else, look up in the [SDK Reference Manual](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual).
- Always close the device (`FDwfDeviceCloseAll()`); the template does this.
- Do not change anything that drives voltage (wavegen, supplies, DIO outputs) without the user's confirmation of wiring.
- Prefer the official sample for the exact feature, found in the SDK `samples/py` folder, when a skill points to one.

## Docs

- [WaveForms SDK Reference Manual](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [WaveForms SDK Getting Started](https://digilent.com/reference/test-and-measurement/guides/waveforms-sdk-getting-started)
- [WaveForms home](https://digilent.com/reference/software/waveforms/waveforms-3/start)
