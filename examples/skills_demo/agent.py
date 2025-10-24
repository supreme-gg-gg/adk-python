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

"""
Example agent demonstrating shell-based Skills integration with ADK.

This agent shows both approaches using a single shell tool for all skills operations.
"""

from pathlib import Path

from google.adk import Agent
from google.adk.apps.app import App
from google.adk.skills import SkillsPlugin, SkillsToolset

# Get the path to the skills directory
SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Approach 1: Agent with SkillsToolset (per-agent skills)
agent_with_toolset = Agent(
    model="gemini-2.0-flash",
    name="skills_shell_agent",
    description="Agent that uses skills through shell commands",
    instruction="""
    You are a helpful assistant with access to specialized skills through shell commands.
    
    Use the shell tool with standard commands:
    - `ls skills/` to discover available skills
    - `head -n 20 skills/SKILL_NAME/SKILL.md` to view skill descriptions
    - `cat skills/SKILL_NAME/SKILL.md` to load full skill content when relevant
    - `cat skills/SKILL_NAME/file.md` to load additional skill files
    - `cd skills/SKILL_NAME && python scripts/script.py` to execute skill scripts
    - `find skills/SKILL_NAME -type f` to list all files in a skill
    
    Always start with `ls skills/` to discover what skills are available, then
    load appropriate skill content when users ask for help with matching tasks.
    
    Execute skill scripts for deterministic operations like data processing.
    """,
    tools=[SkillsToolset(skills_directory=SKILLS_DIR)],
)

# Approach 2: Agent for use with SkillsPlugin (global skills)
agent_with_plugin = Agent(
    model="gemini-2.0-flash",
    name="skills_plugin_agent",
    description="Agent that uses skills through the SkillsPlugin shell tool",
    instruction="""
    You are a helpful assistant with access to specialized skills.
    
    Skills are automatically available through shell commands. Use the shell tool
    to interact with skills using standard commands like:
    
    - `ls skills/` to see available skills
    - `cat skills/SKILL_NAME/SKILL.md` to load skill content
    - `cd skills/SKILL_NAME && python scripts/script.py` to run scripts
    
    The shell tool provides secure access to the skills directory. Use standard
    shell commands when relevant to help users with specialized tasks.
    """,
)

# Create app with SkillsPlugin
app_with_plugin = App(
    name="skills_shell_demo",
    root_agent=agent_with_plugin,
    plugins=[SkillsPlugin(skills_directory=SKILLS_DIR)],
)

# Export the main agent (toolset approach) for CLI usage
root_agent = agent_with_toolset
