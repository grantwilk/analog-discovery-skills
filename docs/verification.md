# Verification

What each skill's code has been run against. Tested with WaveForms 3.25.1 on Windows 11, Python 3.11.

- **Demo**: simulated Analog Discovery 3 (API usage only; the data is not meaningful).
- **Unwired**: a real Analog Discovery 2 with nothing connected to the pins (API usage on real hardware; signals are not meaningful).
- **Loopback**: a real Analog Discovery 2 with the wiring described in the table (results are meaningful).

| Skill | Demo | Unwired | Loopback |
| --- | --- | --- | --- |
| `ad-install` | n/a | pass | n/a |
| `ad-connect` | pass | pass | n/a |
| `ad-device-config` | pass | pass | n/a |
| `ad-scope` | pass | pass | not tested |
| `ad-scope-record` | pass | pass | not tested |
| `ad-spectrum` | pass | pass | not tested |
| `ad-stimulus-response` | skipped (not emulated) | pass | not tested: `W1` to `1+` |
| `ad-wavegen` | pass | not run | not tested: `W1` to `1+` |
| `ad-wavegen-custom` | pass | not run | not tested: `W1` to `1+` |
| `ad-supplies` | pass | not run | not tested: `V+` to `1+` |
| `ad-network-analyzer` | pass | not run | not tested: RC filter, `W1` to `1+` and filter input, output to `2+` |
| `ad-impedance` | pass | not run | not tested: reference resistor and a known part |
| `ad-static-io` | pass | not run | not tested: `DIO0` to `DIO1` |
| `ad-logic-analyzer` | pass | pass | not tested: `DIO0` driven by `ad-pattern-generator` |
| `ad-pattern-generator` | pass | not run | not tested: `DIO0` to `DIO1` |
| `ad-uart` | pass | not run | not tested: `DIO0` to `DIO1` |
| `ad-spi` | pass | not run | not tested: `DIO2` to `DIO3` |
| `ad-i2c` | skipped (no bus) | not run | not tested: needs pull-ups and an I2C device |
| `ad-can` | pass | not run | not tested: needs a CAN transceiver and second node |
| `ad-protocol-spy` | pass | pass | not tested: needs I2C traffic |
| `ad-decode-capture` | pass | n/a | unit tests with synthetic waveforms |
| `ad-save-and-plot` | pass | n/a | n/a |
| `ad-user-handoff`, `ad-troubleshoot`, `ad-overview` | n/a | n/a | n/a |

"Not run" means the skill drives voltage (wavegen, supplies, DIO outputs) and was deliberately not run with unknown wiring.

Update this table whenever a skill's code changes or a new test is run.
