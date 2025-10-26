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

from google.genai import types

from ..tools.base_tool import BaseTool
from ..tools.tool_context import ToolContext

logger = logging.getLogger("google_adk." + __name__)


class SkillsShellTool(BaseTool):
    """Generic shell tool for skills operations with security constraints."""

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
    }

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
        "reboot",
        "shutdown",
        "dd",
        "mount",
        "umount",
        "alias",
        "export",
        "source",
        ".",
        "eval",
        "exec",
    }

    def __init__(self, skills_directory: str | Path):
        super().__init__(
            name="shell",
            description=(
                "Execute sandboxed shell commands for skills operations, file access, and script execution. "
                "Use standard commands like 'ls skills/', 'cat skills/SKILL_NAME/SKILL.md', "
                "or 'cd skills/SKILL_NAME && python scripts/script.py'"
            ),
        )
        self.skills_directory = Path(skills_directory).resolve()
        if not self.skills_directory.exists():
            raise ValueError(
                f"Skills directory does not exist: {self.skills_directory}"
            )

    def _get_declaration(self) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "command": types.Schema(
                        type=types.Type.STRING,
                        description="Shell command to execute. Must be a safe, whitelisted command.",
                    )
                },
                required=["command"],
            ),
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> str:
        command = args.get("command", "").strip()
        if not command:
            return "Error: No command provided"

        try:
            parsed_commands = self._parse_and_validate_command(command)
            result = await self._execute_command_safely(parsed_commands)
            logger.info(f"Executed shell command: {command}")
            return result
        except Exception as e:
            error_msg = f"Error executing command '{command}': {e}"
            logger.error(error_msg)
            return error_msg

    def _parse_and_validate_command(self, command: str) -> List[List[str]]:
        if "&&" in command:
            parts = [part.strip() for part in command.split("&&")]
        else:
            parts = [command]

        parsed_parts = []
        for part in parts:
            parsed_part = shlex.split(part)
            validation_error = self._validate_command_part(parsed_part)
            if validation_error:
                raise ValueError(validation_error)
            parsed_parts.append(parsed_part)
        return parsed_parts

    def _validate_command_part(self, command_parts: List[str]) -> Union[str, None]:
        if not command_parts:
            return "Empty command"

        base_command = command_parts[0]

        if base_command in self.DANGEROUS_COMMANDS:
            return f"Command '{base_command}' is not allowed for security reasons."

        if base_command not in self.SAFE_COMMANDS:
            return f"Command '{base_command}' is not in the allowed list."

        for arg in command_parts[1:]:
            if ".." in arg:
                return "Directory traversal using '..' is not allowed."

            # Further validation to ensure paths are within the skills directory
            if arg.startswith("/"):
                return "Absolute paths are not allowed."

        return None

    async def _execute_command_safely(self, parsed_commands: List[List[str]]) -> str:
        # This method uses os.chdir, which can have side effects in concurrent environments.
        # For this implementation, we accept the risk for simplicity, but a more robust
        # solution might involve managing subprocess CWD without global state changes.
        original_cwd = os.getcwd()
        output_parts = []
        current_cwd = self.skills_directory

        try:
            os.chdir(current_cwd)

            for i, command_parts in enumerate(parsed_commands):
                if i > 0:
                    output_parts.append(f"\n--- Command {i + 1} ---")

                if command_parts[0] == "cd":
                    if len(command_parts) > 1:
                        new_dir = (current_cwd / command_parts[1]).resolve()
                        # Security check: ensure new_dir is within skills_directory
                        if (
                            self.skills_directory not in new_dir.parents
                            and new_dir != self.skills_directory
                        ):
                            raise ValueError(
                                "Cannot cd outside of the skills directory."
                            )
                        current_cwd = new_dir
                        os.chdir(current_cwd)
                        output_parts.append(
                            f"Changed directory to {current_cwd.relative_to(self.skills_directory)}"
                        )
                    continue

                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=current_cwd,
                )

                if result.returncode != 0:
                    output = result.stderr or result.stdout
                    error_output = (
                        f"Command failed with exit code {result.returncode}:\n{output}"
                    )
                    output_parts.append(error_output)
                    break
                else:
                    output = result.stdout or f"Warning: {result.stderr}"
                    output_parts.append(
                        output.strip()
                        if output.strip()
                        else "Command completed successfully."
                    )

            return "\n".join(output_parts)

        except subprocess.TimeoutExpired:
            return "Command execution timed out (30s limit exceeded)"
        except Exception as e:
            return f"Error executing command: {e}"
        finally:
            os.chdir(original_cwd)
