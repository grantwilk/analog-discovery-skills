# Analog Discovery Agent Skills

Atomic, concise skills that let an AI agent do from Python everything a human does in the [Digilent WaveForms](https://digilent.com/reference/software/waveforms/waveforms-3/start) GUI with an Analog Discovery: oscilloscope, waveform generator, logic analyzer, pattern generator, static I/O, power supplies, spectrum, network and impedance analysis, and UART, SPI, I2C, and CAN.

The skills only wrap the official WaveForms SDK (`dwf`, used through `ctypes`). They contain exact commands and working code, and link to Digilent's own documentation for everything else.

> This is an independent community project. It is not affiliated with, endorsed by, or sponsored by Digilent or NI. "Digilent", "Analog Discovery", and "WaveForms" are trademarks of their respective owners. The skills run code that drives real voltages on real hardware; read the code and confirm wiring before running it.

## Skills

Start with `ad-overview`, which indexes everything.

| Area | Skills |
| --- | --- |
| Setup | `ad-install`, `ad-connect`, `ad-device-config`, `ad-troubleshoot` |
| Working with the user | `ad-user-handoff` |
| Analog | `ad-scope`, `ad-scope-record`, `ad-wavegen`, `ad-wavegen-custom`, `ad-supplies`, `ad-spectrum`, `ad-network-analyzer`, `ad-impedance`, `ad-stimulus-response` |
| Digital | `ad-static-io`, `ad-logic-analyzer`, `ad-pattern-generator` |
| Protocols | `ad-uart`, `ad-spi`, `ad-i2c`, `ad-can`, `ad-protocol-spy`, `ad-decode-capture` |
| Output | `ad-save-and-plot` |

## Install

**Cursor:** install this repository as a plugin (see Cursor's [plugins reference](https://cursor.com/docs/reference/plugins)), or copy the repository folder into `~/.cursor/plugins/local/analog-discovery-agent-skills`.

**Other agents:** each folder under `skills/` is a standard `SKILL.md` skill. Copy or link the folders into your agent's skills directory.

**Your machine:** the skills need the WaveForms SDK and Python 3.11 or newer. The `ad-install` skill covers Windows, macOS, and Linux.

## Documentation

- [docs/usage.md](docs/usage.md): how the skills work together and how agents should use them.
- [docs/folders.md](docs/folders.md): repository layout.
- [docs/development.md](docs/development.md): adding skills and running the checks.
- [docs/verification.md](docs/verification.md): what each skill's code has been tested against.
- [CONTRIBUTING.md](CONTRIBUTING.md): branching and release process.

## License

[MIT](LICENSE)
