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
Example agent demonstrating shell-based Skills with comprehensive system prompt.
"""

from pathlib import Path

from google.adk import Agent
from google.adk.apps.app import App
from google.adk.skills import SkillsPlugin, generate_shell_skills_system_prompt

# Get the path to the skills directory
SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Agent with comprehensive shell-based skills system prompt
agent_with_full_prompt = Agent(
    model="gemini-2.0-flash",
    name="skills_shell_expert_agent",
    description="Expert agent with comprehensive shell-based skills guidance",
    instruction=generate_shell_skills_system_prompt(SKILLS_DIR),
)

# Agent with minimal instruction (skills guidance added by plugin)
agent_with_minimal_prompt = Agent(
    model="gemini-2.0-flash",
    name="skills_minimal_agent",
    description="Agent with minimal instruction, shell skills added by plugin",
    instruction="""
    You are a helpful assistant. Use your available tools and skills to help users
    with their tasks. Be efficient and provide accurate, helpful responses.
    """,
)

# Create apps with SkillsPlugin
app_with_full_prompt = App(
    name="skills_shell_expert_demo",
    root_agent=agent_with_full_prompt,
    plugins=[SkillsPlugin(skills_directory=SKILLS_DIR)],
)

app_with_minimal_prompt = App(
    name="skills_minimal_demo",
    root_agent=agent_with_minimal_prompt,
    plugins=[SkillsPlugin(skills_directory=SKILLS_DIR)],
)

# Export for CLI usage
root_agent = agent_with_full_prompt
