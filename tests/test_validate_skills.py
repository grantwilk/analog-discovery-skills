"""Tests for the skill validator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from validate_skills import SkillValidator  # noqa: E402


class TestSkillValidator:
    """Tests for SkillValidator."""

    def test_repository_skills_pass(self) -> None:
        """Every skill in this repository passes validation."""

        validator = SkillValidator()
        assert validator.run() == 0
        assert validator.errors == []

    def test_rejects_name_mismatch(self, tmp_path: Path) -> None:
        """A frontmatter name that differs from the folder name is reported."""

        skill = tmp_path / "ad-example"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: other\ndescription: Does a thing.\n---\n"
            "See [docs](https://digilent.com/reference).\n",
            encoding="utf-8",
        )
        validator = SkillValidator()
        validator._validate_skill(skill)
        assert any("must equal the folder name" in error for error in validator.errors)
