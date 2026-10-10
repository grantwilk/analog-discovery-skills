---
name: ad-save-and-plot
description: Save Analog Discovery scope or logic data to CSV and plot it to a PNG with matplotlib so the agent and user can inspect the result. Use after any capture.
---

# Save and plot

Prereq: samples already captured (`ad-scope`, `ad-logic-analyzer`), `pip install numpy matplotlib`. Run headless: use the `Agg` backend and save to a file, then open or embed the PNG.

```python
# body: standalone, after a capture: ch1 / ch2 are lists of volts, hz is the sample rate
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(len(ch1)) / hz
np.savetxt("capture.csv", np.column_stack([t, ch1, ch2]), delimiter=",", header="t_s,ch1_v,ch2_v", comments="")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t * 1e3, ch1, label="CH1")
ax.plot(t * 1e3, ch2, label="CH2")
ax.set_xlabel("time (ms)")
ax.set_ylabel("volts")
ax.grid(True)
ax.legend()
fig.tight_layout()
fig.savefig("capture.png", dpi=120)
```

- Logic data: save each bit as its own column (`(samples >> k) & 1`) and plot with `ax.step(t, bit + 2 * k, where="post")` to stack channels.
- Bode plots: `ax.semilogx(freqs, gain_db)`.
- Always report scale, units, and sample rate alongside the image; the PNG alone does not carry them.
- Write outputs to a scratch or project `captures/` folder, not into the skills directory.

## Docs

- [matplotlib pyplot reference](https://matplotlib.org/stable/api/pyplot_summary.html)
