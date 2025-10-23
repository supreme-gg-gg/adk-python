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

from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Skill(BaseModel):
    """Represents a skill with its metadata and content.

    A skill is a structured folder containing instructions, scripts, and resources
    that agents can load dynamically to improve performance on specialized tasks.
    Skills follow the progressive disclosure pattern where metadata is loaded first,
    then full content, and finally additional referenced files as needed.
    """

    name: str
    """The unique name/identifier of the skill."""

    description: str
    """A description of what the skill does and when to use it."""

    license: Optional[str] = None
    """Optional license information for the skill."""

    skill_directory: Path
    """The directory path where the skill files are located."""

    content: Optional[str] = None
    """The main skill content from SKILL.md (loaded on demand)."""

    referenced_files: Dict[str, str] = Field(default_factory=dict)
    """Cache of referenced files that have been loaded."""

    available_files: List[str] = Field(default_factory=list)
    """List of additional files available in the skill directory."""

    def __init__(self, **data):
        super().__init__(**data)
        self._discover_available_files()

    def _discover_available_files(self) -> None:
        """Discover all files in the skill directory."""
        if not self.skill_directory.exists():
            return

        for file_path in self.skill_directory.rglob("*"):
            if file_path.is_file() and file_path.name != "SKILL.md":
                relative_path = file_path.relative_to(self.skill_directory)
                self.available_files.append(str(relative_path))

    def load_content(self) -> str:
        """Load the main skill content from SKILL.md.

        Returns:
          The main skill content (markdown body after frontmatter).
        """
        if self.content is not None:
            return self.content

        skill_file = self.skill_directory / "SKILL.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"SKILL.md not found in {self.skill_directory}")

        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove YAML frontmatter if present
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                self.content = parts[2].strip()
            else:
                self.content = content
        else:
            self.content = content

        return self.content

    def load_file(self, file_path: str) -> str:
        """Load a specific file from the skill directory.

        Args:
          file_path: Relative path to the file within the skill directory.

        Returns:
          The content of the requested file.

        Raises:
          FileNotFoundError: If the requested file doesn't exist.
        """
        if file_path in self.referenced_files:
            return self.referenced_files[file_path]

        full_path = self.skill_directory / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File {file_path} not found in skill {self.name}")

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.referenced_files[file_path] = content
            return content
        except UnicodeDecodeError:
            # Handle binary files
            with open(full_path, "rb") as f:
                binary_content = f.read()
            # For now, return a placeholder for binary files
            content = f"[Binary file: {file_path}, size: {len(binary_content)} bytes]"
            self.referenced_files[file_path] = content
            return content

    def get_script_path(self, script_name: str) -> Optional[Path]:
        """Get the full path to a script file in the skill directory.

        Args:
          script_name: Name of the script file (e.g., 'extract_form_fields.py').

        Returns:
          Full path to the script file, or None if not found.
        """
        # Check in scripts/ subdirectory first
        script_path = self.skill_directory / "scripts" / script_name
        if script_path.exists():
            return script_path

        # Check in root of skill directory
        script_path = self.skill_directory / script_name
        if script_path.exists():
            return script_path

        return None

    def list_scripts(self) -> List[str]:
        """List all Python scripts available in the skill.

        Returns:
          List of script file names.
        """
        scripts = []

        # Check scripts/ subdirectory
        scripts_dir = self.skill_directory / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.py"):
                scripts.append(f"scripts/{script_file.name}")

        # Check root directory
        for script_file in self.skill_directory.glob("*.py"):
            scripts.append(script_file.name)

        return scripts

    def to_metadata_dict(self) -> Dict[str, str]:
        """Convert skill to metadata dictionary for agent context.

        Returns:
          Dictionary with skill metadata for progressive disclosure.
        """
        return {
            "name": self.name,
            "description": self.description,
            "license": self.license or "",
            "available_files": ", ".join(self.available_files)
            if self.available_files
            else "None",
            "scripts": ", ".join(self.list_scripts())
            if self.list_scripts()
            else "None",
        }
