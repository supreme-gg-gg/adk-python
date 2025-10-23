# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for SkillLoader functionality."""

import pytest
import tempfile
from pathlib import Path

from google.adk.skills.skill_loader import SkillLoader


class TestSkillLoader:
    """Test SkillLoader functionality."""

    def test_discover_skills(self):
        """Test skill discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test skills
            skill1_dir = temp_path / "skill1"
            skill1_dir.mkdir()
            (skill1_dir / "SKILL.md").write_text(
                "---\nname: skill1\ndescription: Test skill 1\n---\nContent"
            )

            skill2_dir = temp_path / "skill2"
            skill2_dir.mkdir()
            (skill2_dir / "SKILL.md").write_text(
                "---\nname: skill2\ndescription: Test skill 2\n---\nContent"
            )

            # Create directory without SKILL.md (should be ignored)
            (temp_path / "not_a_skill").mkdir()

            loader = SkillLoader(temp_path)
            skills = loader.discover_skills()

            assert len(skills) == 2
            assert "skill1" in skills
            assert "skill2" in skills
            assert "not_a_skill" not in skills

    def test_load_skill_metadata(self):
        """Test loading skill metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test skill with complete metadata
            skill_dir = temp_path / "test-skill"
            skill_dir.mkdir()
            skill_content = """---
name: test-skill
description: A test skill for unit testing
license: Apache 2.0
---
# Test Skill

This is test content."""

            (skill_dir / "SKILL.md").write_text(skill_content)

            loader = SkillLoader(temp_path)
            metadata = loader.load_skill_metadata("test-skill")

            assert metadata["name"] == "test-skill"
            assert metadata["description"] == "A test skill for unit testing"
            assert metadata["license"] == "Apache 2.0"

    def test_load_skill_metadata_missing_required_fields(self):
        """Test error handling for missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create skill missing required fields
            skill_dir = temp_path / "bad-skill"
            skill_dir.mkdir()
            skill_content = """---
license: Apache 2.0
---
# Bad Skill"""

            (skill_dir / "SKILL.md").write_text(skill_content)

            loader = SkillLoader(temp_path)

            with pytest.raises(ValueError, match="missing required 'name' field"):
                loader.load_skill_metadata("bad-skill")

    def test_load_skill_metadata_invalid_yaml(self):
        """Test error handling for invalid YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create skill with invalid YAML
            skill_dir = temp_path / "invalid-skill"
            skill_dir.mkdir()
            skill_content = """---
name: invalid-skill
description: [unclosed list
---
# Invalid Skill"""

            (skill_dir / "SKILL.md").write_text(skill_content)

            loader = SkillLoader(temp_path)

            with pytest.raises(ValueError, match="Invalid YAML frontmatter"):
                loader.load_skill_metadata("invalid-skill")

    def test_load_skill(self):
        """Test loading complete skill object."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test skill
            skill_dir = temp_path / "complete-skill"
            skill_dir.mkdir()
            skill_content = """---
name: complete-skill
description: A complete test skill
---
# Complete Skill

This skill has content and files."""

            (skill_dir / "SKILL.md").write_text(skill_content)
            (skill_dir / "reference.md").write_text("Reference content")

            loader = SkillLoader(temp_path)
            skill = loader.load_skill("complete-skill")

            assert skill.name == "complete-skill"
            assert skill.description == "A complete test skill"
            assert skill.skill_directory == skill_dir
            assert "reference.md" in skill.available_files

    def test_load_all_skills(self):
        """Test loading all skills."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple test skills
            for i in range(3):
                skill_dir = temp_path / f"skill{i}"
                skill_dir.mkdir()
                skill_content = f"""---
name: skill{i}
description: Test skill {i}
---
Content for skill {i}"""
                (skill_dir / "SKILL.md").write_text(skill_content)

            loader = SkillLoader(temp_path)
            skills = loader.load_all_skills()

            assert len(skills) == 3
            for i in range(3):
                assert f"skill{i}" in skills
                assert skills[f"skill{i}"].name == f"skill{i}"

    def test_validate_skill(self):
        """Test skill validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create valid skill
            valid_dir = temp_path / "valid-skill"
            valid_dir.mkdir()
            (valid_dir / "SKILL.md").write_text("""---
name: valid-skill
description: A valid skill
---
Content""")

            # Create invalid skill (name mismatch)
            invalid_dir = temp_path / "invalid-skill"
            invalid_dir.mkdir()
            (invalid_dir / "SKILL.md").write_text("""---
name: different-name
description: Name doesn't match directory
---
Content""")

            loader = SkillLoader(temp_path)

            # Valid skill should have no issues
            issues = loader.validate_skill("valid-skill")
            assert len(issues) == 0

            # Invalid skill should have issues
            issues = loader.validate_skill("invalid-skill")
            assert len(issues) > 0
            assert any("name mismatch" in issue for issue in issues)
