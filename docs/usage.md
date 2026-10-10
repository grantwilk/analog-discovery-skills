# Usage

How agents and people use these skills.

## Design

- **Atomic:** one task per skill, so an agent loads only what it needs.
- **Concise:** a skill holds the critical commands and code, not explanations. Details live in Digilent's documentation, which every skill links to.
- **One template:** every code example is a `# body` block that goes inside the template in `ad-connect`. That template loads the SDK on any OS, opens the device, and always closes it.
- **Human in the loop:** the user does the wiring. Skills that drive voltage tell the agent to send a wiring message first (`ad-user-handoff`).

## Typical Flow

1. `ad-install` once per machine.
2. `ad-connect` to list devices and start a script.
3. Pick the skill for the task (see the index in `ad-overview`).
4. `ad-user-handoff` for the wiring message; wait for the user.
5. Run, read numbers, plot with `ad-save-and-plot`.
6. `ad-troubleshoot` when something fails.

## Testing Without Hardware

The SDK can simulate devices. `ad-connect` shows how to open a demo device, so an agent can check its code before asking the user to wire anything. Demo data is simulated and meaningless; it validates API usage only.

## SDK Version Notes

- Skills use `ctypes` against the installed `dwf` library, so they follow whatever version the user has installed.
- Digilent's bundled samples contain stale calls (`numpy.float`, `time.clock`). The skills use current equivalents.
- The skills use the constants from the installed `dwfconstants.py`; the validator checks every function and constant name against the installed SDK headers.
