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
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Set, Union

from distutils.cmd import Command
from google.genai import types

from ..tools.base_tool import BaseTool
from ..tools.tool_context import ToolContext

logger = logging.getLogger("google_adk." + __name__)


class SkillsShellTool(BaseTool):
    """Generic shell tool for skills operations with security constraints.

    This tool provides shell command execution with skills directory context
    and safety constraints. It's designed to replace multiple specialized
    skill tools with a single, flexible shell interface.
    """

    # Whitelist of safe commands that can be executed
    SAFE_COMMANDS: Set[str] = {
        "ls",
        "cat",
        "head",
        "tail",
        "find",
        "grep",
        "wc",
        "sort",
        "uniq",
        "python",
        "python3",
        "pip",
        "cd",
        "pwd",
        "echo",
        "which",
        "file",
        "uv",
        "uvx",
        "npm",
        "npx",
        "yarn",
        "bun",
    }

    # Blacklist of dangerous commands that should never be executed
    DANGEROUS_COMMANDS: Set[str] = {
        "rm",
        "rmdir",
        "mv",
        "cp",
        "chmod",
        "chown",
        "sudo",
        "su",
        "kill",
        "killall",
        "pkill",
        "reboot",
        "shutdown",
        "dd",
        "fdisk",
        "mount",
        "umount",
        "format",
        "mkfs",
        "fsck",
        "crontab",
        "at",
        "batch",
        "nohup",
        "disown",
        "bg",
        "fg",
        "jobs",
        "alias",
        "unalias",
        "export",
        "unset",
        "source",
        ".",
        "eval",
        "exec",
    }

    def __init__(self, skills_directory: str | Path):
        """Initialize the skills shell tool.

        Args:
          skills_directory: Path to the skills directory.
        """
        super().__init__(
            name="shell",
            description=(
                "Execute shell commands for skills operations, file access, and script execution. "
                "Use standard shell commands like 'ls skills/', 'cat skills/SKILL_NAME/SKILL.md', "
                "or 'cd skills/SKILL_NAME && python scripts/script.py'"
            ),
        )
        self.skills_directory = Path(skills_directory).absolute()

        # Ensure skills directory exists
        if not self.skills_directory.exists():
            raise ValueError(
                f"Skills directory does not exist: {self.skills_directory}"
            )

    def _get_declaration(self) -> types.FunctionDeclaration:
        """Get the function declaration for this tool."""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "command": types.Schema(
                        type=types.Type.STRING,
                        description=(
                            "Shell command to execute. Use standard commands like 'ls', 'cat', "
                            "'find', 'python', etc. Commands are executed in the skills directory context."
                        ),
                    )
                },
                required=["command"],
            ),
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> str:
        """Execute a shell command with skills context and security constraints.

        Args:
          args: Dictionary containing the 'command' to execute.
          tool_context: The tool execution context.

        Returns:
          Command output or error message.
        """
        command = args.get("command", "").strip()
        if not command:
            return "Error: No command provided"

        try:
            # Parse and validate command
            parsed_command = self._parse_and_validate_command(command)

            # Execute command with skills context
            result = await self._execute_command_safely(parsed_command, tool_context)

            logger.info(f"Executed shell command: {command}")
            return result

        except Exception as e:
            error_msg = f"Error executing command '{command}': {e}"
            logger.error(error_msg)
            return error_msg

    def _parse_and_validate_command(self, command: str) -> List[List[str]]:
        """Parse and validate a shell command for security.

        Args:
          command: Raw shell command string.

        Returns:
          Parsed command list or error message string.
        """
        try:
            # Handle compound commands (cd && python)
            if "&&" in command:
                parts = [part.strip() for part in command.split("&&")]
                parsed_parts = []
                for part in parts:
                    parsed_part = shlex.split(part)
                    validation_error = self._validate_command_part(parsed_part)
                    if validation_error:
                        raise ValueError(validation_error)
                    parsed_parts.append(parsed_part)
                return parsed_parts
            else:
                # Single command
                parsed = shlex.split(command)
                validation_error = self._validate_command_part(parsed)
                if validation_error:
                    raise ValueError(validation_error)
                return [parsed]

        except ValueError as e:
            raise ValueError(f"Error parsing command: {e}")

    def _validate_command_part(self, command_parts: List[str]) -> Union[str, None]:
        """Validate a single command part for security.

        Args:
          command_parts: Parsed command parts.

        Returns:
          Error message if invalid, None if valid.
        """
        if not command_parts:
            return "Empty command"

        base_command = command_parts[0]

        # Check against dangerous commands
        if base_command in self.DANGEROUS_COMMANDS:
            return f"Command '{base_command}' is not allowed for security reasons"

        # Check against safe commands (allow python/python3 with any path)
        if base_command not in self.SAFE_COMMANDS and not base_command.endswith(
            "python"
        ):
            return f"Command '{base_command}' is not in the allowed commands list"

        # Additional validation for specific commands
        if base_command == "python" or base_command == "python3":
            # Ensure Python scripts are executed from skills directory
            if len(command_parts) > 1:
                script_path = Path(command_parts[1])
                if script_path.is_absolute():
                    # Check if absolute path is within skills directory
                    try:
                        script_path.resolve().relative_to(self.skills_directory)
                    except ValueError:
                        return f"Python script must be within skills directory: {self.skills_directory}"

        return None

    async def _execute_command_safely(
        self, parsed_commands: List[List[str]], tool_context: ToolContext
    ) -> str:
        """Execute parsed commands safely with proper working directory.

        Args:
          parsed_commands: List of parsed command parts.
          tool_context: Tool execution context.

        Returns:
          Command output.
        """
        # Set working directory to skills directory
        original_cwd = os.getcwd()
        output_parts = []

        try:
            os.chdir(self.skills_directory)

            for i, command_parts in enumerate(parsed_commands):
                if i > 0:
                    output_parts.append(f"\n--- Command {i + 1} ---")

                # Execute single command
                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=self.skills_directory,
                )

                if result.returncode != 0:
                    error_output = f"Command failed with exit code {result.returncode}:\n{result.stderr}"
                    output_parts.append(error_output)
                    break  # Stop on first failure in compound command
                else:
                    if result.stdout.strip():
                        output_parts.append(result.stdout.strip())
                    elif result.stderr.strip():
                        output_parts.append(f"Warning: {result.stderr.strip()}")
                    else:
                        output_parts.append(
                            "Command completed successfully (no output)"
                        )

            return (
                "\n".join(output_parts)
                if output_parts
                else "Commands completed successfully"
            )

        except subprocess.TimeoutExpired:
            return "Command execution timed out (30s limit exceeded)"
        except Exception as e:
            return f"Error executing command: {e}"
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def get_skills_context(self) -> str:
        """Get context information about available skills for agent instructions.

        Returns:
          Formatted skills context for agent instructions.
        """
        try:
            # List skills directories
            skills = []
            for item in self.skills_directory.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    # Try to read skill description
                    try:
                        with open(item / "SKILL.md", "r", encoding="utf-8") as f:
                            content = f.read()
                        # Extract description from YAML frontmatter
                        if content.startswith("---\n"):
                            parts = content.split("---\n", 2)
                            if len(parts) >= 3:
                                import yaml

                                try:
                                    metadata = yaml.safe_load(parts[1])
                                    description = metadata.get(
                                        "description", "No description"
                                    )
                                    skills.append(f"- {item.name}: {description}")
                                except:
                                    skills.append(f"- {item.name}: Available")
                            else:
                                skills.append(f"- {item.name}: Available")
                        else:
                            skills.append(f"- {item.name}: Available")
                    except:
                        skills.append(f"- {item.name}: Available")

            if skills:
                return f"Available skills in {self.skills_directory}:\n" + "\n".join(
                    skills
                )
            else:
                return f"No skills found in {self.skills_directory}"

        except Exception as e:
            return f"Error reading skills directory: {e}"
