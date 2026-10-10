"""Runs every `# body` code block in the skills inside the ad-connect template on a device."""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


class SnippetRunner:
    """Executes skill code examples against a WaveForms demo device or a real device."""

    ROOT = Path(__file__).resolve().parent.parent
    CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)
    OPEN_LINE = (
        "dwf.FDwfDeviceOpen(-1, byref(hdwf))   # -1 = first device; use an index to pick another"
    )
    PASS_LINE = "    pass  # paste a `# body` block here"
    DEMO_SKIPPED = {
        "ad-i2c": "demo device has no I2C bus",
        "ad-stimulus-response": "demo device does not emulate wavegen-to-scope triggering",
    }
    PREAMBLES = {
        "ad-save-and-plot": (
            "import math\nhz = 1e6\nch1 = [math.sin(i / 50) for i in range(2000)]\n"
            "ch2 = [0.5 * math.sin(i / 50 + 1) for i in range(2000)]\n"
        ),
        "ad-decode-capture": (
            "import sys\nsys.path.insert(0, r'{skill}')\nrate = 1e6\nsamples = [3] * 100\n"
        ),
    }

    def __init__(self, demo: bool, only: list[str], timeout: float) -> None:
        """
        Initializes the runner.

        Args:
            demo (bool): True to open a WaveForms demo device instead of real hardware.
            only (list[str]): Skill names to run; empty runs all.
            timeout (float): Seconds allowed per snippet.
        """

        self.demo = demo
        self.only = only
        self.timeout = timeout
        self.template = self._template()

    def _template(self) -> str:
        """
        Reads the connection template from the ad-connect skill.

        Returns:
            str: The template source.
        """

        text = (self.ROOT / "skills" / "ad-connect" / "SKILL.md").read_text(encoding="utf-8")
        return self.CODE_BLOCK.findall(text)[0]

    def _bodies(self, skill: Path) -> list[tuple[int, str]]:
        """
        Extracts the `# body` blocks of a skill, chaining blocks that continue a previous one.

        Args:
            skill (Path): Skill folder.

        Returns:
            list[tuple[int, str]]: Block index and runnable body source.
        """

        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        bodies: list[tuple[int, str]] = []
        previous = ""
        for index, block in enumerate(self.CODE_BLOCK.findall(text), start=1):
            if not block.startswith("# body"):
                continue
            first = block.splitlines()[0]
            source = previous + "\n" + block if "after" in first else block
            bodies.append((index, source))
            previous = block
        return bodies

    def _demo_open(self) -> str:
        """
        Builds source that opens a demo device in place of the template's open call.

        Returns:
            str: Replacement source.
        """

        return (
            "_n = c_int()\n"
            "dwf.FDwfEnum(enumfilterDemo.value | enumfilterType.value, byref(_n))\n"
            "_pick = -1\n"
            "for _i in range(_n.value):\n"
            "    _name = create_string_buffer(64)\n"
            "    dwf.FDwfEnumDeviceName(_i, _name)\n"
            "    if b'Discovery 3' in _name.value:\n"
            "        _pick = _i\n"
            "dwf.FDwfDeviceOpen(_pick, byref(hdwf))"
        )

    def _assemble(self, skill: Path, body: str) -> str:
        """
        Embeds a body in the template.

        Args:
            skill (Path): Skill folder.
            body (str): Body source.

        Returns:
            str: A complete script.
        """

        source = self.template
        if self.demo:
            source = source.replace(self.OPEN_LINE, self._demo_open())
        preamble = self.PREAMBLES.get(skill.name, "").replace("{skill}", str(skill))
        indented = "".join(f"    {line}\n" for line in (preamble + body).splitlines())
        return source.replace(self.PASS_LINE + "\n", indented)

    def run(self) -> int:
        """
        Runs all selected snippets.

        Returns:
            int: Process exit code, 0 if every snippet passed.
        """

        failures = 0
        for skill in sorted((self.ROOT / "skills").iterdir()):
            if self.only and skill.name not in self.only:
                continue
            if self.demo and skill.name in self.DEMO_SKIPPED:
                print(f"SKIP {skill.name}: {self.DEMO_SKIPPED[skill.name]}")
                continue
            for index, body in self._bodies(skill):
                script = self._assemble(skill, body)
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "snippet.py"
                    path.write_text(script, encoding="utf-8")
                    try:
                        result = subprocess.run(
                            [sys.executable, str(path)],
                            capture_output=True,
                            text=True,
                            timeout=self.timeout,
                            cwd=folder,
                        )
                        ok, output = result.returncode == 0, result.stdout + result.stderr
                    except subprocess.TimeoutExpired:
                        ok, output = False, "timed out"
                print(f"{'PASS' if ok else 'FAIL'} {skill.name} block {index}")
                if not ok:
                    failures += 1
                    print("   " + output.strip().replace("\n", "\n   ")[-600:])
                elif output.strip():
                    print("   " + output.strip().replace("\n", "\n   ")[-300:])
        print(f"{failures} failure(s)")
        return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="use a WaveForms demo device")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("skills", nargs="*", help="skill names to run (default: all)")
    args = parser.parse_args()
    sys.exit(SnippetRunner(args.demo, args.skills, args.timeout).run())
