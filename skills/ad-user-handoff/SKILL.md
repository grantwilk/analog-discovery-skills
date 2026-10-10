---
name: ad-user-handoff
description: How to tell the user exactly what to wire, connect, or check on an Analog Discovery before running a script, and how to report results afterward. Use before any step that needs physical wiring, power, or user judgement.
---

# Handing off to the human

The agent cannot touch the hardware. Before running anything that depends on wiring, give the user one message in this format and wait for confirmation.

```
Wiring for <goal>  (device: <name>, serial <SN>)
  <Analog Discovery pin>  ->  <target point>      <purpose>
  <Analog Discovery pin>  ->  <target point>      <purpose>
  GND                     ->  <target ground>      common ground (required)
Settings: <voltage levels, ranges, rates the script will use>
Risks: <anything the script will drive: voltage on W1/W2, V+ / V-, DIO output>
Reply "ready" when connected. Do not connect anything above 5 V to a pin unless noted.
```

## Pin names (Analog Discovery 2 and 3 pod connector)

| Name on the pin header | Use |
| --- | --- |
| `1+`, `1-` / `2+`, `2-` | Scope channel 1 and 2, differential inputs. `-` goes to ground unless measuring across a component |
| `W1`, `W2` | Wavegen outputs |
| `V+`, `V-` | Programmable supplies |
| `DIO 0` to `DIO 15` | Digital I/O, 3.3 V logic |
| `T1`, `T2` | Trigger in or out |
| `GND` | Ground (several pins; all common) |

Pin positions and color coding differ by model and cable: point the user to the pinout in the [Analog Discovery 2](https://digilent.com/reference/test-and-measurement/analog-discovery-2/reference-manual) or [Analog Discovery 3](https://digilent.com/reference/test-and-measurement/analog-discovery-3/reference-manual) reference manual instead of describing physical positions.

## Rules

- Always specify a ground connection for every signal measured or driven.
- Say which pins are inputs and which are outputs. Anything that drives (`W1`, `W2`, `V+`, `V-`, DIO outputs) is a risk to the target; state the voltage and current.
- If the target runs at a different logic level than 3.3 V, say so and ask for a level shifter before proceeding.
- Never assume a connection was made. Verify when possible: read a DC level with `ad-scope`, a pin state with `ad-static-io`, or a bus address scan with `ad-i2c`.
- After the run, report in plain terms: what was measured, with numbers and units, and whether it passes the user's expectation. Offer the plot (`ad-save-and-plot`).
- Ask the user to power-cycle or physically intervene only for things the agent cannot do (changing jumpers, moving probes, applying external power).
