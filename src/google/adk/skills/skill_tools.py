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
from typing import List

from ..tools.tool_context import ToolContext
from .skill_manager import SkillManager

logger = logging.getLogger("google_adk." + __name__)


def create_skill_tools(skills_directory: str | Path) -> List:
    """Create skill management tools for a given skills directory.

    Args:
      skills_directory: Path to the skills directory.

    Returns:
      List of skill management function tools.
    """
    skill_manager = SkillManager(skills_directory)

    # Load skills metadata at creation time
    skill_manager.load_skill_metadata()

    async def list_available_skills(tool_context: ToolContext) -> str:
        """List all available skills with their descriptions.

        This provides the first level of progressive disclosure by showing skill
        metadata without loading full content.

        Returns:
          Formatted list of available skills with descriptions.
        """
        skills_summary = skill_manager.get_skill_metadata_summary()

        # Store available skills in context for reference
        tool_context.state["available_skills"] = skill_manager.list_skills()

        logger.info("Skills discovery requested")
        return skills_summary

    async def load_skill_content(skill_name: str, tool_context: ToolContext) -> str:
        """Load the full content of a specific skill.

        This provides the second level of progressive disclosure by loading the
        complete SKILL.md content for a specific skill.

        Args:
          skill_name: Name of the skill to load.

        Returns:
          Full skill content from SKILL.md.
        """
        try:
            content = skill_manager.load_skill_content(skill_name)

            # Store loaded skill in context
            if "loaded_skills" not in tool_context.state:
                tool_context.state["loaded_skills"] = []
            if skill_name not in tool_context.state["loaded_skills"]:
                tool_context.state["loaded_skills"].append(skill_name)

            logger.info(f"Loaded skill content: {skill_name}")
            return f"# Skill: {skill_name}\n\n{content}"

        except Exception as e:
            error_msg = f"Failed to load skill '{skill_name}': {e}"
            logger.error(error_msg)
            return error_msg

    async def load_skill_file(
        skill_name: str, file_path: str, tool_context: ToolContext
    ) -> str:
        """Load a specific file from a skill directory.

        This provides the third level of progressive disclosure by loading
        additional files referenced in the skill content.

        Args:
          skill_name: Name of the skill.
          file_path: Relative path to the file within the skill directory.

        Returns:
          Content of the requested file.
        """
        try:
            content = skill_manager.load_skill_file(skill_name, file_path)

            # Store loaded files in context
            if "loaded_skill_files" not in tool_context.state:
                tool_context.state["loaded_skill_files"] = []
            file_key = f"{skill_name}/{file_path}"
            if file_key not in tool_context.state["loaded_skill_files"]:
                tool_context.state["loaded_skill_files"].append(file_key)

            logger.info(f"Loaded file {file_path} from skill {skill_name}")
            return f"# File: {skill_name}/{file_path}\n\n{content}"

        except Exception as e:
            error_msg = (
                f"Failed to load file '{file_path}' from skill '{skill_name}': {e}"
            )
            logger.error(error_msg)
            return error_msg

    async def list_skill_files(skill_name: str, tool_context: ToolContext) -> str:
        """List all available files in a skill directory.

        Args:
          skill_name: Name of the skill.

        Returns:
          Formatted list of available files.
        """
        try:
            skill = skill_manager.get_skill(skill_name)
            if not skill:
                return f"Skill '{skill_name}' not found"

            if not skill.available_files:
                return f"No additional files found in skill '{skill_name}'"

            files_list = "\n".join(f"- {file}" for file in skill.available_files)
            return f"Available files in skill '{skill_name}':\n{files_list}"

        except Exception as e:
            error_msg = f"Failed to list files for skill '{skill_name}': {e}"
            logger.error(error_msg)
            return error_msg

    # Return the function tools
    return [
        list_available_skills,
        load_skill_content,
        load_skill_file,
        list_skill_files,
    ]
