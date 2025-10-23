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

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

try:
    import yaml
except ImportError:
    yaml = None

from .skill import Skill

logger = logging.getLogger("google_adk." + __name__)


class SkillLoader:
    """Loads and parses skills from directories.

    The SkillLoader discovers skill directories, parses SKILL.md files with YAML
    frontmatter, and creates Skill objects for use by the skills system.
    """

    def __init__(self, skills_directory: str | Path):
        """Initialize the skill loader.

        Args:
          skills_directory: Path to the directory containing skill folders.
        """
        self.skills_directory = Path(skills_directory)
        if not self.skills_directory.exists():
            raise ValueError(f"Skills directory does not exist: {skills_directory}")

    def discover_skills(self) -> List[str]:
        """Discover all skill directories.

        Returns:
          List of skill directory names.
        """
        skills = []
        for item in self.skills_directory.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skills.append(item.name)
        return skills

    def load_skill_metadata(self, skill_name: str) -> Dict[str, str]:
        """Load only the metadata from a skill's SKILL.md file.

        Args:
          skill_name: Name of the skill directory.

        Returns:
          Dictionary containing the YAML frontmatter metadata.

        Raises:
          FileNotFoundError: If SKILL.md doesn't exist.
          ValueError: If YAML frontmatter is invalid.
        """
        skill_dir = self.skills_directory / skill_name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse YAML frontmatter
        if not content.startswith("---\n"):
            raise ValueError(f"SKILL.md in {skill_name} missing YAML frontmatter")

        parts = content.split("---\n", 2)
        if len(parts) < 3:
            raise ValueError(f"SKILL.md in {skill_name} has malformed YAML frontmatter")

        if yaml is None:
            raise ValueError("PyYAML library not installed. Run: pip install pyyaml")

        try:
            metadata = yaml.safe_load(parts[1])
            if not isinstance(metadata, dict):
                raise ValueError(
                    f"YAML frontmatter in {skill_name} is not a dictionary"
                )

            # Ensure required fields
            if "name" not in metadata:
                raise ValueError(
                    f"SKILL.md in {skill_name} missing required 'name' field"
                )
            if "description" not in metadata:
                raise ValueError(
                    f"SKILL.md in {skill_name} missing required 'description' field"
                )

            return metadata

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter in {skill_name}: {e}")

    def load_skill(self, skill_name: str) -> Skill:
        """Load a complete skill object.

        Args:
          skill_name: Name of the skill directory.

        Returns:
          Skill object with metadata loaded.
        """
        skill_dir = self.skills_directory / skill_name
        metadata = self.load_skill_metadata(skill_name)

        skill = Skill(
            name=metadata["name"],
            description=metadata["description"],
            license=metadata.get("license"),
            skill_directory=skill_dir,
        )

        logger.debug(f"Loaded skill: {skill.name}")
        return skill

    def load_all_skills(self) -> Dict[str, Skill]:
        """Load all skills from the skills directory.

        Returns:
          Dictionary mapping skill names to Skill objects.
        """
        skills = {}
        skill_names = self.discover_skills()

        for skill_name in skill_names:
            try:
                skill = self.load_skill(skill_name)
                skills[skill.name] = skill
                logger.info(f"Loaded skill: {skill.name}")
            except Exception as e:
                logger.error(f"Failed to load skill {skill_name}: {e}")
                continue

        logger.info(f"Loaded {len(skills)} skills total")
        return skills

    def validate_skill(self, skill_name: str) -> List[str]:
        """Validate a skill and return any issues found.

        Args:
          skill_name: Name of the skill to validate.

        Returns:
          List of validation issues (empty if valid).
        """
        issues = []
        skill_dir = self.skills_directory / skill_name

        # Check if directory exists
        if not skill_dir.exists():
            issues.append(f"Skill directory {skill_name} does not exist")
            return issues

        # Check if SKILL.md exists
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            issues.append(f"SKILL.md file missing in {skill_name}")
            return issues

        # Validate metadata
        try:
            metadata = self.load_skill_metadata(skill_name)

            # Check required fields
            if not metadata.get("name"):
                issues.append(f"Missing or empty 'name' field in {skill_name}")
            if not metadata.get("description"):
                issues.append(f"Missing or empty 'description' field in {skill_name}")

            # Check name consistency
            if metadata.get("name") != skill_name:
                issues.append(
                    f"Skill name mismatch: directory is '{skill_name}' but "
                    f"metadata name is '{metadata.get('name')}'"
                )

        except Exception as e:
            issues.append(f"Failed to parse metadata in {skill_name}: {e}")

        return issues
