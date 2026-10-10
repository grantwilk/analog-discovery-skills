"""Validates the skills in this plugin: structure, Python syntax, and SDK name accuracy."""

import ast
import glob
import json
import re
import sys
from pathlib import Path


class SkillValidator:
    """Checks every skill and the plugin manifest, reporting all problems found."""

    ROOT = Path(__file__).resolve().parent.parent
    MAX_LINES = 140
    NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
    CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)
    FUNCTION = re.compile(r"\bFDwf[A-Za-z0-9]+")
    CONSTANT = re.compile(
        r"\b(?:acqmode|trigsrc|trigtype|func(?=[A-Z])|enumfilter|DwfState|DwfTrigger|DwfDigitalOut"
        r"|DwfAnalog|DwfParam|AnalogOutNode|DECI)[A-Za-z0-9]*\b"
    )
    SAMPLE = re.compile(r"\b[A-Za-z0-9]+_[A-Za-z0-9_]+\.py\b")
    SDK_GLOBS = [
        r"C:\Program Files*\Digilent\WaveFormsSDK",
        "/usr/share/digilent/waveforms",
        "/Applications/WaveForms.app/Contents/Resources/SDK",
    ]

    def __init__(self) -> None:
        """Initializes the validator and locates the installed SDK, if any."""

        self.errors: list[str] = []
        self.sdk = self._find_sdk()

    def _find_sdk(self) -> Path | None:
        """
        Finds an installed WaveForms SDK.

        Returns:
            Path | None: The SDK folder, or None if it is not installed.
        """

        for pattern in self.SDK_GLOBS:
            for match in glob.glob(pattern):
                return Path(match)
        return None

    def _fail(self, where: str, message: str) -> None:
        """
        Records a problem.

        Args:
            where (str): File or skill the problem belongs to.
            message (str): What is wrong.
        """

        self.errors.append(f"{where}: {message}")

    def _validate_manifest(self) -> None:
        """Checks that the plugin manifest parses and has the required fields."""

        path = self.ROOT / ".cursor-plugin" / "plugin.json"
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            self._fail(str(path), f"unreadable manifest: {error}")
            return
        for key in ("name", "description", "version", "license", "repository"):
            if not manifest.get(key):
                self._fail(str(path), f"missing '{key}'")

    def _frontmatter(self, skill: Path, text: str) -> tuple[dict[str, str], str]:
        """
        Splits a SKILL.md into its frontmatter and body.

        Args:
            skill (Path): Skill folder, for error messages.
            text (str): Full file contents.

        Returns:
            tuple[dict[str, str], str]: Frontmatter fields and the markdown body.
        """

        match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        if not match:
            self._fail(skill.name, "missing frontmatter")
            return {}, text
        fields = {}
        for line in match.group(1).splitlines():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        return fields, match.group(2)

    def _validate_names(self, skill: Path, body: str) -> None:
        """
        Checks that SDK functions, constants, and sample files mentioned in a skill exist.

        Args:
            skill (Path): Skill folder, for error messages.
            body (str): Markdown body.
        """

        if self.sdk is None:
            return
        header = (self.sdk / "inc" / "dwf.h").read_text(encoding="utf-8", errors="ignore")
        constants = (self.sdk / "samples" / "py" / "dwfconstants.py").read_text(encoding="utf-8")
        samples = {p.name for p in (self.sdk / "samples" / "py").glob("*.py")}
        for name in sorted(set(self.FUNCTION.findall(body))):
            if not re.search(rf"\b{name}\b", header):
                self._fail(skill.name, f"unknown SDK function {name}")
        for name in sorted(set(self.CONSTANT.findall(body))):
            if not re.search(rf"^{name}\s*=", constants, re.MULTILINE):
                self._fail(skill.name, f"unknown SDK constant {name}")
        for name in sorted(set(self.SAMPLE.findall(body))):
            if name not in samples:
                self._fail(skill.name, f"unknown sample {name}")

    def _validate_code(self, skill: Path, body: str) -> None:
        """
        Checks that every Python code block parses.

        Args:
            skill (Path): Skill folder, for error messages.
            body (str): Markdown body.
        """

        for index, block in enumerate(self.CODE_BLOCK.findall(body), start=1):
            try:
                ast.parse(block)
            except SyntaxError as error:
                self._fail(skill.name, f"python block {index} does not parse: {error}")

    def _validate_skill(self, skill: Path) -> None:
        """
        Checks one skill folder.

        Args:
            skill (Path): Skill folder.
        """

        path = skill / "SKILL.md"
        if not path.exists():
            self._fail(skill.name, "missing SKILL.md")
            return
        text = path.read_text(encoding="utf-8")
        fields, body = self._frontmatter(skill, text)
        if fields.get("name") != skill.name:
            self._fail(skill.name, "frontmatter name must equal the folder name")
        if not self.NAME_PATTERN.match(skill.name):
            self._fail(skill.name, "folder name must be lowercase kebab-case")
        description = fields.get("description", "")
        if not description or len(description) > 400:
            self._fail(skill.name, "description must exist and be at most 400 characters")
        if len(text.splitlines()) > self.MAX_LINES:
            self._fail(skill.name, f"longer than {self.MAX_LINES} lines; keep skills concise")
        if "digilent.com" not in body and skill.name != "ad-save-and-plot":
            self._fail(skill.name, "must link to Digilent documentation")
        self._validate_code(skill, body)
        self._validate_names(skill, body)

    def run(self) -> int:
        """
        Validates the whole plugin.

        Returns:
            int: Process exit code, 0 if everything passed.
        """

        self._validate_manifest()
        skills = sorted(p for p in (self.ROOT / "skills").iterdir() if p.is_dir())
        if not skills:
            self._fail("skills", "no skills found")
        for skill in skills:
            self._validate_skill(skill)
        for error in self.errors:
            print(f"ERROR {error}")
        sdk_note = "SDK name checks on" if self.sdk else "SDK not installed: name checks skipped"
        print(f"{len(skills)} skills checked ({sdk_note}), {len(self.errors)} problem(s)")
        return 1 if self.errors else 0


if __name__ == "__main__":
    sys.exit(SkillValidator().run())
