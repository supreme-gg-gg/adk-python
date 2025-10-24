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
from typing import Optional

from google.genai import types

from ..agents.base_agent import BaseAgent
from ..agents.callback_context import CallbackContext
from ..plugins.base_plugin import BasePlugin
from .skills_shell_tool import SkillsShellTool

logger = logging.getLogger("google_adk." + __name__)


class SkillsPlugin(BasePlugin):
    """Plugin that provides Anthropic-style Skills functionality via shell tool.

    This plugin provides global skills access by:
    1. Adding a shell tool for skills operations to all LLM agents
    2. Injecting skills context into agent instructions
    3. Enabling shell-based progressive disclosure of skills

    The plugin uses a single shell tool instead of multiple specialized tools,
    making the system simpler and more flexible.
    """

    def __init__(self, skills_directory: str | Path, name: str = "skills_plugin"):
        """Initialize the skills plugin.

        Args:
          skills_directory: Path to directory containing skill folders.
          name: Name of the plugin instance.
        """
        super().__init__(name)
        self.skills_directory = Path(skills_directory)

        # Create shell tool for skills operations
        self.shell_tool = SkillsShellTool(skills_directory)

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> Optional[types.Content]:
        """Add shell tool and skills context to agents.

        This provides skills functionality by:
        1. Adding shell tool for skills operations
        2. Enhancing agent instructions with skills context and usage guidance
        """
        # Only work with LLM agents
        from ..agents.llm_agent import LlmAgent

        if not isinstance(agent, LlmAgent):
            return None

        # Add shell tool if not already present
        tool_names = set()
        for tool_union in agent.tools:
            if hasattr(tool_union, "name"):
                tool_names.add(tool_union.name)
            elif callable(tool_union) and hasattr(tool_union, "__name__"):
                tool_names.add(tool_union.__name__)

        if "shell" not in tool_names:
            agent.tools.append(self.shell_tool)
            logger.debug(f"Added shell tool to agent: {agent.name}")

        # Add skills context to agent instruction
        if hasattr(agent, "instruction") and isinstance(agent.instruction, str):
            if "Skills available in:" not in agent.instruction:
                skills_context = self._generate_skills_instruction()
                agent.instruction += skills_context
                logger.debug(
                    f"Enhanced agent instruction with skills context: {agent.name}"
                )

        # Add skills availability to callback context state
        callback_context.state["skills_available"] = True
        callback_context.state["skills_directory"] = str(self.skills_directory)

        return None

    def _generate_skills_instruction(self) -> str:
        """Generate skills instruction for agent enhancement."""
        skills_context = self.shell_tool.get_skills_context()

        return f"""

## Skills System - Shell Access

{skills_context}

### Shell Commands for Skills

Use the shell tool with these commands:

**Discovery:**
- `ls skills/` - List all available skills
- `head -n 20 skills/SKILL_NAME/SKILL.md` - View skill metadata and description

**Loading Content:**
- `cat skills/SKILL_NAME/SKILL.md` - Load complete skill content
- `cat skills/SKILL_NAME/reference.md` - Load additional skill files

**Script Execution:**
- `cd skills/SKILL_NAME && python scripts/SCRIPT_NAME.py` - Execute skill scripts
- `find skills/SKILL_NAME -name "*.py"` - List available scripts

**File Operations:**
- `find skills/SKILL_NAME -type f` - List all files in a skill
- `ls -la skills/SKILL_NAME/` - Detailed file listing

### Usage Pattern

1. **Discover**: `shell("ls skills/")` to see available skills
2. **Investigate**: `shell("head -n 20 skills/SKILL_NAME/SKILL.md")` to read descriptions  
3. **Load**: `shell("cat skills/SKILL_NAME/SKILL.md")` when skill is relevant to user's task
4. **Execute**: `shell("cd skills/SKILL_NAME && python scripts/SCRIPT.py")` for automation

Always start with skill discovery and load content progressively as needed."""
