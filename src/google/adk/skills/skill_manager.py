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
from typing import Dict, List, Optional

from .skill import Skill
from .skill_loader import SkillLoader

logger = logging.getLogger("google_adk." + __name__)


class SkillManager:
    """Manages loaded skills and provides progressive disclosure functionality.

    The SkillManager handles the lifecycle of skills, including loading, caching,
    and providing progressive disclosure where metadata is loaded first, followed
    by full content and additional files as needed.
    """

    def __init__(self, skills_directory: str | Path):
        """Initialize the skill manager.

        Args:
          skills_directory: Path to the directory containing skill folders.
        """
        self.skill_loader = SkillLoader(skills_directory)
        self.skills: Dict[str, Skill] = {}
        self._metadata_loaded = False

    def load_skill_metadata(self) -> None:
        """Load metadata for all skills (first level of progressive disclosure).

        This loads only the YAML frontmatter from each skill's SKILL.md file,
        providing enough information for agents to decide which skills are relevant.
        """
        if self._metadata_loaded:
            return

        skill_names = self.skill_loader.discover_skills()
        logger.info(f"Discovered {len(skill_names)} skills")

        for skill_name in skill_names:
            try:
                skill = self.skill_loader.load_skill(skill_name)
                self.skills[skill.name] = skill
            except Exception as e:
                logger.error(f"Failed to load skill metadata for {skill_name}: {e}")
                continue

        self._metadata_loaded = True
        logger.info(f"Loaded metadata for {len(self.skills)} skills")

    def get_skill_metadata_summary(self) -> str:
        """Get a formatted summary of all skill metadata for agent context.

        Returns:
          Formatted string with skill names and descriptions.
        """
        if not self._metadata_loaded:
            self.load_skill_metadata()

        if not self.skills:
            return "No skills available."

        lines = ["Available Skills:"]
        for skill in self.skills.values():
            lines.append(f"- {skill.name}: {skill.description}")

        return "\n".join(lines)

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name.

        Args:
          skill_name: Name of the skill to retrieve.

        Returns:
          Skill object if found, None otherwise.
        """
        if not self._metadata_loaded:
            self.load_skill_metadata()

        return self.skills.get(skill_name)

    def load_skill_content(self, skill_name: str) -> str:
        """Load the full content of a skill (second level of progressive disclosure).

        Args:
          skill_name: Name of the skill to load content for.

        Returns:
          The full skill content from SKILL.md.

        Raises:
          ValueError: If skill not found.
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        content = skill.load_content()
        logger.debug(f"Loaded content for skill: {skill_name}")
        return content

    def load_skill_file(self, skill_name: str, file_path: str) -> str:
        """Load a specific file from a skill (third level of progressive disclosure).

        Args:
          skill_name: Name of the skill.
          file_path: Relative path to the file within the skill directory.

        Returns:
          Content of the requested file.

        Raises:
          ValueError: If skill not found.
          FileNotFoundError: If file not found.
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        content = skill.load_file(file_path)
        logger.debug(f"Loaded file {file_path} from skill: {skill_name}")
        return content

    def get_skill_scripts(self, skill_name: str) -> List[str]:
        """Get list of available scripts for a skill.

        Args:
          skill_name: Name of the skill.

        Returns:
          List of script file names.

        Raises:
          ValueError: If skill not found.
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        return skill.list_scripts()

    def get_skill_script_path(
        self, skill_name: str, script_name: str
    ) -> Optional[Path]:
        """Get the full path to a skill script.

        Args:
          skill_name: Name of the skill.
          script_name: Name of the script file.

        Returns:
          Full path to the script file, or None if not found.

        Raises:
          ValueError: If skill not found.
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        return skill.get_script_path(script_name)

    def list_skills(self) -> List[str]:
        """List all available skill names.

        Returns:
          List of skill names.
        """
        if not self._metadata_loaded:
            self.load_skill_metadata()

        return list(self.skills.keys())

    def validate_all_skills(self) -> Dict[str, List[str]]:
        """Validate all skills and return any issues found.

        Returns:
          Dictionary mapping skill names to lists of validation issues.
        """
        skill_names = self.skill_loader.discover_skills()
        validation_results = {}

        for skill_name in skill_names:
            issues = self.skill_loader.validate_skill(skill_name)
            if issues:
                validation_results[skill_name] = issues

        return validation_results

    def reload_skills(self) -> None:
        """Reload all skills from disk.

        This clears the current skill cache and reloads everything from the
        skills directory.
        """
        self.skills.clear()
        self._metadata_loaded = False
        self.load_skill_metadata()
        logger.info("Reloaded all skills")
