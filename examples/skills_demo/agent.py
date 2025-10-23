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
Example agent demonstrating Skills integration with ADK.

This agent shows both approaches:
1. Using SkillsPlugin for global skills access
2. Using SkillsToolset for per-agent skills access
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
    name="skills_toolset_agent",
    description="Agent that uses skills through the SkillsToolset",
    instruction="""
    You are a helpful assistant with access to specialized skills through tools.
    
    Use the list_available_skills tool to see what skills are available.
    Use load_skill_content to get the full content of a skill when relevant to the user's request.
    Use load_skill_file to get additional context files when needed.
    Use execute_skill_script to run skill scripts for deterministic operations.
    
    Always check what skills are available first, then load the appropriate skill
    content when the user asks for help with tasks that match a skill's description.
    """,
    tools=[SkillsToolset(skills_directory=SKILLS_DIR)],
)

# Approach 2: Agent for use with SkillsPlugin (global skills)
agent_with_plugin = Agent(
    model="gemini-2.0-flash",
    name="skills_plugin_agent",
    description="Agent that uses skills through the SkillsPlugin",
    instruction="""
    You are a helpful assistant with access to specialized skills.
    
    Skills are automatically available to you through tools. When a user asks for help with
    a task that matches one of your available skills, you can:
    
    - Use list_available_skills() to see what skills are available
    - Use load_skill_content(skill_name) to get the full skill content
    - Use load_skill_file(skill_name, file_path) for additional context files
    - Use execute_skill_script(skill_name, script_name) to run skill scripts
    
    The available skills and their descriptions will be provided in your context.
    Use the tools when relevant to help users with specialized tasks.
    """,
)

# Create app with SkillsPlugin
app_with_plugin = App(
    name="skills_plugin_demo",
    root_agent=agent_with_plugin,
    plugins=[SkillsPlugin(skills_directory=SKILLS_DIR)],
)

# Export the main agent (toolset approach) for CLI usage
root_agent = agent_with_toolset
