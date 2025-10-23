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
from .skill_manager import SkillManager
from .skill_system_prompt import get_skills_instruction_addition
from .skill_tools import create_skill_tools

logger = logging.getLogger("google_adk." + __name__)


class SkillsPlugin(BasePlugin):
    """Plugin that provides Anthropic-style Skills functionality to ADK agents.

    This plugin provides global skills access by:
    1. Injecting skill metadata into agent context at startup
    2. Automatically adding skill management tools to LLM agents
    3. Providing progressive disclosure through explicit tool calls

    The plugin uses ADK's existing tool and code execution systems rather than
    fragile regex parsing or subprocess execution.
    """

    def __init__(self, skills_directory: str | Path, name: str = "skills_plugin"):
        """Initialize the skills plugin.

        Args:
          skills_directory: Path to directory containing skill folders.
          name: Name of the plugin instance.
        """
        super().__init__(name)
        self.skill_manager = SkillManager(skills_directory)
        self.skills_directory = Path(skills_directory)

        # Load skill metadata at initialization
        self.skill_manager.load_skill_metadata()

        # Create skill tools that will be added to agents
        self.skill_tools = create_skill_tools(skills_directory)

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> Optional[types.Content]:
        """Inject skill metadata and tools into agent context.

        This provides skills functionality by:
        1. Adding skill metadata to agent context
        2. Dynamically adding skill management tools to LLM agents
        """
        # Only work with LLM agents
        from ..agents.llm_agent import LlmAgent

        if not isinstance(agent, LlmAgent):
            return None

        # Get skill metadata summary
        skills_summary = self.skill_manager.get_skill_metadata_summary()

        # Add skills context to the callback context state
        callback_context.state["skills_available"] = True
        callback_context.state["skills_summary"] = skills_summary

        # Enhance agent instruction with skills guidance
        skills_instruction = get_skills_instruction_addition(self.skill_manager)
        if hasattr(agent, "instruction") and isinstance(agent.instruction, str):
            # Add skills guidance to existing instruction if not already present
            if "Skills Available" not in agent.instruction:
                agent.instruction += skills_instruction

        # Add skill tools to the agent if not already present
        existing_tool_names = set()

        # Check existing tools to avoid duplicates
        for tool_union in agent.tools:
            if callable(tool_union) and hasattr(tool_union, "__name__"):
                existing_tool_names.add(tool_union.__name__)

        # Add missing skill tools
        tools_to_add = [
            tool
            for tool in self.skill_tools
            if tool.__name__ not in existing_tool_names
        ]

        if tools_to_add:
            # Temporarily add tools to the agent for this invocation
            # Note: This modifies the agent instance, but only for skill tools
            agent.tools.extend(tools_to_add)
            logger.debug(
                f"Added {len(tools_to_add)} skill tools to agent: {agent.name}"
            )

        logger.debug(f"Injected skills metadata for agent: {agent.name}")
        return None
