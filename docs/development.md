# Development

How to add or change skills and run the same checks as CI.

## Prerequisites

- **Python 3.11+**
- `python -m pip install pytest ruff numpy matplotlib`
- For full validation: the WaveForms SDK installed (see `skills/ad-install/SKILL.md`). Without it, SDK name checks are skipped (CI runs this way).
- Optional hardware: an Analog Discovery. Demo devices need no hardware.

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md`. The folder name must match the frontmatter `name`, in lowercase kebab-case with an `ad-` prefix.
2. Write a `description` that says what the skill does and when to use it (400 characters at most).
3. Keep it short: critical info, exact commands, exact code, and links into Digilent's documentation. Stay under 140 lines.
4. Write code examples as `# body` blocks that run inside the `ad-connect` template. Start the block with `# body: runs inside the ad-connect template`. Mark a block that continues the previous one with the word "after" in its first line.
5. Use only functions and constants that exist in the installed SDK (`inc/dwf.h`, `samples/py/dwfconstants.py`).
6. Add the skill to the tables in [folders.md](folders.md) and the root [README.md](../README.md), and to the index in `skills/ad-overview/SKILL.md`.
7. Run the checks below and record the result in [verification.md](verification.md).

## Checks

```powershell
ruff check .
python tools/validate_skills.py
python -m pytest
python tools/run_snippets.py --demo
```

| Command | What it does |
| --- | --- |
| `ruff check .` | Lints the Python in `tools/`, `tests/`, and `decode.py`. |
| `python tools/validate_skills.py` | Checks manifests, frontmatter, length, Digilent links, code syntax, and (with the SDK installed) every `FDwf*` function, constant, and sample file name. |
| `python -m pytest` | Runs unit tests for the decoder and tools. |
| `python tools/run_snippets.py --demo` | Runs every `# body` block on a simulated Analog Discovery 3. Pass skill names to run only those, or omit `--demo` to run on real hardware. |

Real hardware runs drive voltages. Run only skills that are safe for the current wiring, and record results in `docs/verification.md`.

## CI

Pushes to `main`, tags starting with `v`, and pull requests into `main` run `.github/workflows/ci.yml`: lint, validate (without SDK name checks), and unit tests. SDK-dependent checks and snippet runs happen locally because the SDK is not redistributable.
