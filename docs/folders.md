# Folders

Repository layout.

| Path | Purpose |
| --- | --- |
| `.cursor-plugin/plugin.json` | Cursor plugin manifest; points at `skills/`. |
| `.claude-plugin/plugin.json` | Equivalent manifest for agents that use that location. Keep it in sync with the Cursor one. |
| `skills/<name>/SKILL.md` | One skill per folder; the folder name equals the `name` in the frontmatter. |
| `skills/ad-decode-capture/decode.py` | Offline UART, SPI, and I2C decoder bundled with its skill. |
| `tools/validate_skills.py` | Checks manifests, skill structure, code syntax, and SDK name accuracy. |
| `tools/run_snippets.py` | Runs every skill code example on a demo or real device. |
| `tests/` | Unit tests for `decode.py` and the tools. |
| `docs/` | Project documentation. |
| `.cursor/rules/rules.mdc` | Rules for agents working on this repository. |
| `.github/` | CI workflow and pull request template. |

## Skills

| Skill | Purpose |
| --- | --- |
| `ad-overview` | Index and entry point. |
| `ad-install` | Install WaveForms and the SDK. |
| `ad-connect` | Script template; list and open devices. |
| `ad-device-config` | Choose buffer configurations. |
| `ad-user-handoff` | Wiring messages for the user. |
| `ad-troubleshoot` | Diagnose failures. |
| `ad-scope` | Oscilloscope capture and triggers. |
| `ad-scope-record` | Long oscilloscope recordings. |
| `ad-wavegen` | Standard waveforms and sweeps. |
| `ad-wavegen-custom` | Arbitrary waveforms. |
| `ad-supplies` | Power supplies and monitors. |
| `ad-spectrum` | FFT of scope data. |
| `ad-network-analyzer` | Bode plots. |
| `ad-impedance` | Impedance, R, L, C. |
| `ad-stimulus-response` | Synchronized output and capture. |
| `ad-static-io` | Digital pin levels. |
| `ad-logic-analyzer` | Digital captures. |
| `ad-pattern-generator` | Digital patterns, clocks, PWM. |
| `ad-uart` | UART send and receive. |
| `ad-spi` | SPI master. |
| `ad-i2c` | I2C master and scan. |
| `ad-can` | CAN send and receive. |
| `ad-protocol-spy` | Passive I2C spy; capture other buses. |
| `ad-decode-capture` | Decode captured protocol traffic. |
| `ad-save-and-plot` | CSV and PNG output. |
